"""
Download list of articles urls from www.brasovultau.ro
to be scraped later by brasovultau_download.py
"""

import asyncio
import aiohttp
import aiofiles

from bs4 import BeautifulSoup

from random import randint
from structlog import get_logger
from devtools import debug


""" const """
OUTFILE = "input/articles-brasovultau.txt"
CATEGORIES_FILES = "input/categories-brasovultau.txt"
BASE_URL = "http://www.brasovultau.ro"
MAX_NUM_CONNECTIONS = 5
MAX_TIMEOUT = 900
UA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
}

""" globals """
log = get_logger()


async def delay(lo=100, delta=900):
    """Async delay for random miliseconds"""
    await asyncio.sleep(randint(lo, lo + delta) / 1000)


"""
var request = $.ajax({
    url: '/bin/paging.php',
    type: "POST",
    data: {
      forPage: forPage,
      currentPage: currentPage
    },

"""


async def main():
    connector = aiohttp.TCPConnector(limit_per_host=MAX_NUM_CONNECTIONS)
    timeout = aiohttp.ClientTimeout(total=MAX_TIMEOUT)
    session = aiohttp.ClientSession(connector=connector, timeout=timeout)

    # read categories start pages from file:
    with open(CATEGORIES_FILES, "r") as f:
        categories = f.read().splitlines()

    articles = set()
    all_articles = []

    # DEBUG
    category = "http://www.brasovultau.ro/categorii/cultura.html"

    has_next_page = True
    async with session.get(category, headers=UA_HEADERS) as resp:
        page = BeautifulSoup(await resp.text(), "lxml")
        page_articles = page.select(".item .item-title a")
        for article in page_articles:
            article_url = article.get("href")
            all_articles.append(article_url)
            articles.add(article_url)

    debug(all_articles)
    debug(articles)
    # with open(OUTFILE, "w") as f:
    #     f.truncate()
    await session.close()
    # -


if __name__ == "__main__":
    asyncio.run(main())
