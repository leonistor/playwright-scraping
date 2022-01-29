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
# VALID_YEARS = [str(year) for year in range(2014, 2022)]
# DEBUG
VALID_YEARS = [str(year) for year in range(2014, 2016)]

UA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
}

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


async def page_soup(session: aiohttp.ClientSession, url: str) -> BeautifulSoup:
    """fetch url and get its soup"""
    await delay()
    async with session.get(url, headers=UA_HEADERS) as resp:
        soup = BeautifulSoup(await resp.text(), "lxml")
    return soup


def get_page_articles(soup: BeautifulSoup):
    result = []
    link_tags = soup.select("article.item-list h2 a")
    for link_tag in link_tags:
        link = link_tag.get("href")
        result.append(link)
    return result


async def get_edition_articles(session: aiohttp.ClientSession, url: str):
    """list of article links in an edition with multiple pages"""
    result = []
    num_pages = None

    log.debug("edition", url=url)

    # process first page of edition
    first_soup = await page_soup(session, url)
    # get num pages
    span_pages = get_content(first_soup, "span.pages")
    span_num_pages = span_pages.split(" ")[-1]
    try:
        num_pages = int(span_num_pages)
    except ValueError as e:
        log.error("oops, invalid num_pages", span_pages=span_pages)
        raise e

    log.debug("edition", num_pages=num_pages)

    # articles for first page
    result.extend(get_page_articles(first_soup))

    # build urls of pages
    pages_urls = [url]
    for page in range(2, num_pages + 1):
        pages_urls.append(f"{url}/page/{page}")
    # extract articles from each page
    for page_url in pages_urls:
        soup = await page_soup(session, page_url)
        log.debug("page", page_url=page_url)
        result.extend(get_page_articles(soup))

    return result
    # -


def is_valid_year(tag: Tag) -> bool:
    text = tag.getText()
    year = text.split(" ")[-1]
    return year in VALID_YEARS


async def main():

    # TODO
    # -----------------
    # - year param back
    # - global outdir aici
    # - task pool din articole
    # - fara poze?
    # -----------------

    connector = aiohttp.TCPConnector(limit_per_host=MAX_NUM_CONNECTIONS)
    session = aiohttp.ClientSession(connector=connector)

    # parse archive page and get links to edtions
    archive = await page_soup(session, f"{BASE_URL}/arhiva")
    all_years_links = archive.select("ul.children li a")
    editions_links = list(filter(is_valid_year, all_years_links))
    editions_urls = []
    for edition in editions_links:
        url = edition.get("href")
        if url:
            editions_urls.append(url)

    # parse each edition and get links to articles
    articles = []
    for edition_url in editions_urls:
        edition_articles = await get_edition_articles(session, edition_url)
        log.debug(
            "edition articles",
            edition_url=edition_url,
            articles_count=len(edition_articles),
        )
        articles.extend(edition_articles)

    debug(articles)
    await session.close()
    # -


if __name__ == "__main__":
    os.makedirs(OUTDIR, exist_ok=True)

    asyncio.run(main())
