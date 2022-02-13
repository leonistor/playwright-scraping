"""
Download PDFs from https://cartigratis.com/categ?page=2
"""

import asyncio
import aiohttp
import aiofiles
from bs4 import BeautifulSoup

from random import randint
from devtools import debug
import logging

""" const """
OUTDIR = "output/robooks/cartigratis"
MAX_NUM_CONNECTIONS = 5
BASE_URL = "https://cartigratis.com"
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
    async with session.get(
        url,
        headers=UA_HEADERS,
        proxy="http://intelnuc:3129",
    ) as resp:
        soup = BeautifulSoup(await resp.text(), "lxml")
    return soup


async def save_pdf(session: aiohttp.ClientSession, url: str):
    await delay()
    async with session.get(
        url,
        headers=UA_HEADERS,
        proxy="http://intelnuc:3129",
    ) as resp:
        if resp.status == 200:
            filename = url.split("/")[-1]
            f = await aiofiles.open(f"{OUTDIR}/{filename}", "wb")
            # TODO: aiohttp.client_exceptions.ClientPayloadError: Response payload is not completed
            await f.write(await resp.read())
            await f.close()
            logging.debug(f"wrote {filename}")
        else:
            logging.error(f"bad download for {url}")


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
        book_urls = []
        for url in [f"{BASE_URL}/categ?page={i}" for i in range(1, 60 + 1)]:
            page = await page_soup(session, url)
            book_tags = page.select("a.product-item-name")
            for book in book_tags:
                book_url = book.get("href")
                book_urls.append(book_url)
        logging.info(f"collected {len(book_urls)} book urls")
        # debug(book_urls)

        with open("input/cartigratis-urls.txt", "w") as f:

            for url in book_urls:
                page = await page_soup(session, url)
                download_tag = page.select_one(
                    ".product-price-and-delivery .product-price a"
                )
                if download_tag:
                    pdf_href = download_tag.get("href")
                    if isinstance(pdf_href, str):
                        pdf_url = f"{pdf_href}\n"
                        f.write(pdf_url)
                        # await save_pdf(session, pdf_url)
                        # logging.info(f"file: {pdf_url}")
                    else:
                        logging.error(f"bad download url {download_tag} for {url}")
                        continue
                else:
                    logging.error(f"bad download tag {download_tag} for {url}")
                    continue
        # - ClientSession

    logging.debug("done")
    # -


if __name__ == "__main__":
    asyncio.run(main())
