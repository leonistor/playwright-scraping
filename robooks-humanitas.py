"""
Download PDFs from https://humanitas.ro/humanitas/colectii/biblioteca-virtuala
"""

import asyncio
import aiohttp
import aiofiles
from bs4 import BeautifulSoup

from random import randint
from devtools import debug
import logging

""" const """
OUTDIR = "output/robooks/humanitas"
MAX_NUM_CONNECTIONS = 5
BASE_URL = "https://humanitas.ro"
MAX_TIMEOUT = 9000
UA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
}


async def delay(lo=100, delta=900):
    """Async delay for random miliseconds"""
    await asyncio.sleep(randint(lo, lo + delta) / 1000)


async def page_soup(session: aiohttp.ClientSession, url: str) -> BeautifulSoup:
    """fetch url and get its soup"""
    await delay()
    async with session.get(url, headers=UA_HEADERS) as resp:
        soup = BeautifulSoup(await resp.text(), "lxml")
    return soup


async def save_pdf(session, outdir: str, image_url: str, image_file: str):
    await delay()
    async with session.get(image_url, headers=UA_HEADERS) as resp:
        if resp.status == 200:
            fimg = await aiofiles.open(f"{outdir}/img/{image_file}", "wb")
            await fimg.write(await resp.read())
            await fimg.close()


async def main():
    logging.basicConfig(
        format="▸ :%(lineno)d %(levelname)s %(message)s",
        level=logging.DEBUG,
        datefmt="%H:%M:%S",
    )
    logging.debug("started")
    connector = aiohttp.TCPConnector(limit_per_host=MAX_NUM_CONNECTIONS)
    timeout = aiohttp.ClientTimeout(total=MAX_TIMEOUT)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        for url in [
            f"{BASE_URL}/humanitas/colectii/biblioteca-virtuala/{i}"
            for i in range(1, 4 + 1)
        ]:
            page = await page_soup(session, url)
            book_tags = page.select(".book_box .book-description a")
            for book in book_tags:
                book_url = book.get("href")
                logging.debug(f"{BASE_URL}{book_url}")
    logging.debug("done")


if __name__ == "__main__":
    asyncio.run(main())
