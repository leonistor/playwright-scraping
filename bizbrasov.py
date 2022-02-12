"""
Download list of articles urls from https://www.monitorulexpres.ro/
to be scraped later.
"""

import asyncio
import aiohttp
import aiofiles
import aiohttp_client_cache.session

from bs4 import BeautifulSoup, Tag

from random import randint
import logging
from devtools import debug


""" const """
OUTFILE = "input/articles-bizbrasov.txt"
BASE_URL = "https://www.bizbrasov.ro/stiri-brasov/stiri-din-judetul-brasov/"
MAX_PAGE = 1440
# MAX_PAGE = 5
MAX_NUM_CONNECTIONS = 5
MAX_TIMEOUT = 3000
UA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
}

""" globals """
logging.basicConfig(
    format="▸ %(levelname)s %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
)


async def delay(lo=100, delta=900):
    """Async delay for random miliseconds"""
    await asyncio.sleep(randint(lo, lo + delta) / 1000)


async def page_soup(session: aiohttp.ClientSession, url: str) -> BeautifulSoup:
    """fetch url and get its soup"""
    await delay()
    async with session.get(
        url,
        headers=UA_HEADERS,
        proxy="http://intelnuc:3129",
    ) as resp:
        soup = BeautifulSoup(await resp.text(), "lxml")
    return soup


async def main():
    logging.info("started")

    urls = [f"{BASE_URL}page/{i}" for i in range(2, 1 + MAX_PAGE)]
    urls.insert(0, BASE_URL)
    debug(urls)
    connector = aiohttp.TCPConnector(limit_per_host=MAX_NUM_CONNECTIONS)
    timeout = aiohttp.ClientTimeout(total=MAX_TIMEOUT)
    async with aiohttp_client_cache.session.CachedSession(
        connector=connector,
        timeout=timeout,
    ) as session, aiofiles.open(OUTFILE, "w") as fout:
        for url in urls:
            page = await page_soup(session, url)
            logging.info(f"url: {url}")
            article_urls = []
            article_tags = page.select(
                ".main-content h2.is-title.post-title a, .main-featured h2.is-title.post-title a"
            )
            for article in article_tags:
                article_url = article.get("href")
                if isinstance(article_url, str):
                    article_urls.append(article_url)
            await fout.write("\n".join(article_urls) + "\n")
        # - url in urls
    logging.info("done!")
    # - main


if __name__ == "__main__":
    asyncio.run(main())
