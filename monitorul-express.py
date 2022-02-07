"""
Download list of articles urls from https://www.monitorulexpres.ro/
to be scraped later.
"""

import asyncio
import aiohttp
import aiofiles

from bs4 import BeautifulSoup

from random import randint
from structlog import get_logger
from devtools import debug


""" const """
OUTFILE = "input/articles-monitorul-express.txt"
CATEGORIES_FILES = "input/categories-monitorul-express.txt"
BASE_URL = "https://www.monitorulexpres.ro/"
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
    category = "https://www.monitorulexpres.ro/category/ultima-ora/"

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
