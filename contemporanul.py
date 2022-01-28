import asyncio
import aiohttp
import aiofiles
import os

from random import randint
from structlog import get_logger
from devtools import debug
from jsonlines import Writer

from bs4 import BeautifulSoup
from bs4.element import Tag

""" const """
MAX_NUM_CONNECTIONS = 5
BASE_URL = "https://www.contemporanul.ro"
OUTDIR = "output/contemporanul/"
VALID_YEARS = [str(year) for year in range(2014, 2022)]

UA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
}
LNAMES = {
    "01": "ianuarie",
    "02": "februarie",
    "03": "martie",
    "04": "aprilie",
    "05": "mai",
    "06": "iunie",
    "07": "iulie",
    "08": "august",
    "09": "septembrie",
    "10": "octombrie",
    "11": "noiembrie",
    "12": "decembrie",
}  # "luni" (months) names

""" globals """
log = get_logger()


async def delay(lo=100, hi=900):
    """async sleep between lo and hi miliseconds"""
    await asyncio.sleep(randint(lo, hi) / 1000)


def get_content(soup: BeautifulSoup | Tag, selector, default="") -> str:
    """get text content of selector from soup"""
    elem = soup.select_one(selector=selector)
    if elem is not None:
        return elem.get_text()
    else:
        return default


async def save_image(session, outdir: str, image_url: str, image_file: str):
    await delay()
    async with session.get(image_url, headers=UA_HEADERS) as resp:
        # log.debug("image", url=image_url, file=image_file, status=resp.status)
        if resp.status == 200:
            fimg = await aiofiles.open(f"{outdir}/img/{image_file}", "wb")
            await fimg.write(await resp.read())
            await fimg.close()


def get_article_links(soup: BeautifulSoup):
    """list of article links in soup of page"""
    result = []
    link_tags = soup.select("article.item-list h2 a")
    # log.debug("link_tags", link_tags=link_tags)
    for link_tag in link_tags:
        link = link_tag.get("href")
        result.append(link)
    return result


async def page_soup(session: aiohttp.ClientSession, url: str) -> BeautifulSoup:
    """fetch url and get its soup"""
    await delay()
    async with session.get(url, headers=UA_HEADERS) as resp:
        soup = BeautifulSoup(await resp.text(), "lxml")
    return soup


def is_valid_year(tag: Tag) -> bool:
    text = tag.getText()
    year = text.split(" ")[-1]
    return year in VALID_YEARS


async def main():
    connector = aiohttp.TCPConnector(limit_per_host=MAX_NUM_CONNECTIONS)
    session = aiohttp.ClientSession(connector=connector)

    # parse archive page and get links to edtions
    archive = await page_soup(session, f"{BASE_URL}/arhiva")
    all_years = archive.select("ul.children li a")
    years = list(filter(is_valid_year, all_years))
    # editions =
    debug(years)

    debug(type(years[0]))

    await session.close()
    # -


if __name__ == "__main__":
    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(f"{OUTDIR}/img", exist_ok=True)

    asyncio.run(main())
