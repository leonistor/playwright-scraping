import asyncio
from distutils.log import debug
import aiohttp
import aiofiles
import os

from structlog import get_logger
from tap import Tap
from jsonlines import Writer

from bs4 import BeautifulSoup
from bs4.element import Tag

""" const """
MAX_NUM_CONNECTIONS = 5
BASE_URL = "https://www.contemporanul.ro/"
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


def get_content(soup: BeautifulSoup | Tag, selector, default="") -> str:
    elem = soup.select_one(selector=selector)
    if elem is not None:
        return elem.get_text()
    else:
        return default


async def save_image(session, outdir: str, image_url: str, image_file: str):
    async with session.get(image_url, headers=UA_HEADERS) as resp:
        # log.debug("image", url=image_url, file=image_file, status=resp.status)
        if resp.status == 200:
            fimg = await aiofiles.open(f"{outdir}/img/{image_file}", "wb")
            await fimg.write(await resp.read())
            await fimg.close()


def get_article_links(soup: BeautifulSoup):
    pass


async def get_luna(luna: str, an: int, outdir: str):
    fout = open(outdir + f"/contemporanul-{an}-{luna}.jsonl", "w")
    writer = Writer(fout)
    # writer.write({"an": an, "luna": luna, "test": "yes"})
    # a "luna" (edition) has about 3 pages listing links to articles
    luna_url = f"{BASE_URL}numere/nr-{luna}-{LNAMES[luna]}-{an}"
    log.debug("luna", when={"an": an, "luna": luna, "url": luna_url})
    # get article links from all the pages of edition
    article_links = []
    num_pages = None
    # get  first page
    connector = aiohttp.TCPConnector(limit_per_host=MAX_NUM_CONNECTIONS)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(luna_url, headers=UA_HEADERS) as resp:
            soup = BeautifulSoup(await resp.text(), "lxml")
    # get num_pages from 'Page x of y'
    span_pages = get_content(
        soup,
        "#main-content > div.content-wrap > div > div.pagination > span.pages",
    )
    span_num_pages = span_pages.split(" ")[-1]
    try:
        num_pages = int(span_num_pages)
    except ValueError as e:
        log.error("oops, invalid num_pages", span_pages=span_pages)
        raise e
    log.debug("num_pages", num_pages=num_pages)
    # TODO: from first page eliminate first item, is archive
    # for this and next pages extend article_links


async def main(an: int, outdir: str):
    luni = []
    for i in range(1, 13):
        luni.append("{:02d}".format(i))
    # TODO: debug
    for luna in luni[:3]:
        await get_luna(luna, an, outdir)


if __name__ == "__main__":

    class SimpleArgParser(Tap):
        an: int = 2014

    args = SimpleArgParser().parse_args()
    outdir = f"output/contemporanul/{args.an}"
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(f"{outdir}/img", exist_ok=True)

    asyncio.run(main(an=args.an, outdir=outdir))
