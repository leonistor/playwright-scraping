"""
Download list of articles urls from https://www.monitorulexpres.ro/
to be scraped later.
"""

import asyncio
from posixpath import split
import aiohttp
import aiofiles

from bs4 import BeautifulSoup, Tag

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
    # debug(categories)

    articles = set()

    # process category start for above articles and num_pages
    category_url = "https://www.monitorulexpres.ro/category/ultima-ora/"
    await delay()
    async with session.get(category_url, headers=UA_HEADERS) as resp:
        page = BeautifulSoup(await resp.text(), "lxml")

        above_articles_tags = page.select(".td-category-pos-above a.td-image-wrap")
        articles.update([article.get("href") for article in above_articles_tags])

        page_articles = page.select(".tdb-numbered-pagination h3.entry-title a")
        articles.update([article.get("href") for article in page_articles])

        num_pages_tag = page.select_one("span.pages")
        num_pages_text = num_pages_tag.text if isinstance(num_pages_tag, Tag) else None
        num_pages_str = num_pages_text.split(" ")[-1] if num_pages_text else "0"
        num_pages = int(num_pages_str)

    # process pages
    debug(num_pages)
    # for num_page in range(2, num_pages):
    for num_page in range(2, 10):
        category_page_url = f"{category_url}page/{num_page}/"
        async with session.get(category_page_url, headers=UA_HEADERS) as resp:
            page = BeautifulSoup(await resp.text(), "lxml")
            page_articles = page.select(".tdb-numbered-pagination h3.entry-title a")
            articles.update([article.get("href") for article in page_articles])

    debug(len(articles))
    with open(OUTFILE, "w") as f:
        f.write("\n".join(articles))
    await session.close()
    # -


if __name__ == "__main__":
    asyncio.run(main())
