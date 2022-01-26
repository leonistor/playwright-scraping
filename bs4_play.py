from email import header
import aiofiles
import aiohttp
import asyncio
import sys, os
import datetime
import jsonlines
from jsonlines import Writer

from loguru import logger

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, BrowserContext, TimeoutError

""" CONFIG """
BASE_URL = "https://books.toscrape.com/"
LASTPAGE = 50
# LASTPAGE = 3


""" GLOBALS """
context: BrowserContext
user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0"
writer: Writer
page_urls = [
    f"{BASE_URL}catalogue/page-{index}.html" for index in range(1, LASTPAGE + 1)
]
outdir = "output/books/" + datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")


def setup_logging():
    logger.remove(0)
    logger.add(
        sys.stderr,
        format="{level.icon}<light-blue>{time:HH:mm:ss}</light-blue> "
        + "<yellow>{level}</yellow> <white>{message}</white>",
    )
    _page_level = logger.level("PAGE", no=38, color="<yellow>", icon="📄")
    _book_level = logger.level("BOOK", no=39, color="<white>", icon="📘")


def setup_output():
    global writer
    os.makedirs(outdir, exist_ok=True)
    fout = open(outdir + "/books.jsonl", "w")
    writer = jsonlines.Writer(fout)


async def start_playwright():
    global context
    global user_agent
    playwright = await async_playwright().start()
    browser = await playwright.firefox.launch(headless=True)
    context = await browser.new_context(
        no_viewport=True,
        accept_downloads=True,
    )
    page = await context.new_page()
    await page.goto(BASE_URL)
    ua = await page.evaluate("navigator.userAgent")
    if ua:
        user_agent = ua


async def stop_playwright():
    global context
    browser = context.browser
    if browser:
        await browser.close()


async def parse_page(session, url):
    headers = {"User-Agent": user_agent}
    async with session.get(url, headers=headers) as response:
        logger.log("PAGE", f">>> {url}")

        html = await response.text()
        soup = BeautifulSoup(html, "lxml")
        # DEBUG
        # for link_tag in soup.select("h3 a")[:3]:
        for link_tag in soup.select("h3 a"):
            link = link_tag.get("href")
            book_url = f"{BASE_URL}catalogue/{link}"
            await parse_book(session, book_url)


async def save_image(session, image_url: str, image_file: str):
    headers = {"User-Agent": user_agent}
    async with session.get(image_url, headers=headers) as resp:
        if resp.status == 200:
            fimg = await aiofiles.open(f"{outdir}/{image_file}", "wb")
            await fimg.write(await resp.read())
            await fimg.close()


async def parse_book(session, book_url):
    global context
    page = await context.new_page()
    await page.goto(book_url)
    logger.log("BOOK", f"{book_url}")

    title = await page.locator("h1").text_content()

    try:
        description = await page.locator("div#product_description + p").text_content()
    except TimeoutError:
        description = ""

    price: str = await page.locator("h1 + p.price_color").text_content() or ""
    price = price.strip("£")
    img_src = await page.locator(
        "#product_gallery > div > div > div > img"
    ).get_attribute("src")
    image_file = ""
    if img_src:
        image_url = BASE_URL + img_src.removeprefix("../../")
        image_file = image_url.split("/")[-1]
        await save_image(session, image_url, image_file)

    book = {
        "title": title,
        "description": description,
        "price": price,
        "image_file": image_file,
    }
    writer.write(book)
    await page.close()


async def main():
    await start_playwright()
    async with aiohttp.ClientSession() as session:
        for url in page_urls:
            await parse_page(session, url)
    await stop_playwright()


setup_logging()
setup_output()
asyncio.run(main())
