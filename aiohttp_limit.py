import asyncio
import aiohttp

from structlog import get_logger

from bs4 import BeautifulSoup

""" const """
MAX_NUM_CONNECTIONS = 5

UA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
}


""" globals """
log = get_logger()


def get_content(soup: BeautifulSoup, selector, default="") -> str:
    elem = soup.select_one(selector=selector)
    if elem is not None:
        return elem.get_text()
    else:
        return default


async def parse_book(url: str, session: aiohttp.ClientSession):
    async with session.get(url, headers=UA_HEADERS) as resp:
        if resp.status == 200:
            soup = BeautifulSoup(await resp.text(), "lxml")
            title = get_content(soup, "h1")
            # description = get_content(soup, "div#product_description + p")
            book = {
                "url": url,
                "title": title,
            }
            log.msg("book ok", book=book)
        else:
            book = {
                "url": url,
                "error": resp.status,
            }
            log.msg("book error", book=book)


async def book_links_from_page(url: str, session: aiohttp.ClientSession):
    async with session.get(url, headers=UA_HEADERS) as resp:
        soup = BeautifulSoup(await resp.text(), "lxml")
        result = []
        links = soup.select("h3 a")
        for link in links:
            link_url = f"https://books.toscrape.com/catalogue/{link.get('href')}"
            result.append(link_url)
        return result


async def main():
    page_urls = [
        f"https://books.toscrape.com/catalogue/page-{index}.html"
        for index in range(1, 6)
    ]

    tasks = []
    connector = aiohttp.TCPConnector(limit_per_host=MAX_NUM_CONNECTIONS)

    async with aiohttp.ClientSession(connector=connector) as session:
        for page_url in page_urls:
            log.msg("page", url=page_url)
            page_links = await book_links_from_page(page_url, session)
            for link in page_links:
                task = asyncio.create_task(
                    parse_book(
                        link,
                        session=session,
                    )
                )
                tasks.append(task)
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
