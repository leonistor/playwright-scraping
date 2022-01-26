import asyncio
from webbrowser import get
import aiohttp

from structlog import get_logger
from tap import Tap

from bs4 import BeautifulSoup
from bs4.element import Tag

""" const """
MAX_NUM_CONNECTIONS = 5
BASE_URL = "https://bzb.ro/"
UA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
}


""" globals """
log = get_logger()


def get_content(soup: BeautifulSoup | Tag, selector, default="") -> str:
    elem = soup.select_one(selector=selector)
    if elem is not None:
        return elem.get_text()
    else:
        return default


async def get_article(
    url: str,
    session: aiohttp.ClientSession,
    section_title: str,
    pub_date: str,
):
    article = {}
    article["url"] = url
    article["section_title"] = section_title
    article["pub_date"] = pub_date

    async with session.get(url, headers=UA_HEADERS) as resp:
        if resp.status == 200:
            soup = BeautifulSoup(await resp.text(), "lxml")
            article["title"] = get_content(soup, "h1")
            article["author"] = get_content(soup, ".a_author > span:nth-child(1)")
        else:
            article["error"] = resp.status
    log.debug("article", article=article)


async def main(edition_id: int):
    edition = {}
    edition["id"] = str(edition_id)

    tasks = []
    connector = aiohttp.TCPConnector(limit_per_host=MAX_NUM_CONNECTIONS)

    async with aiohttp.ClientSession(connector=connector) as session:
        edition_url = f"{BASE_URL}/arhiva/editia/{edition_id}"
        edition["url"] = edition_url
        async with session.get(edition_url, headers=UA_HEADERS) as resp:
            # publication_date
            soup = BeautifulSoup(await resp.text(), "lxml")
            edition_date = get_content(soup, ".archive_index h1").split(" - ")[-1]
            edition["publication_date"] = edition_date
            # sections
            sections = soup.select(".category_holder")
            for section in sections:
                section_title = get_content(section, "h2", default="Default")
                # log.debug("section", title=section_title)
                article_links = section.select("h3 a")
                for link_tag in article_links:
                    link = link_tag.get("href")
                    article_url = f"{BASE_URL}{link}"
                    # log.debug("article", article_url=article_url)
                    task = asyncio.create_task(
                        get_article(
                            article_url,
                            session,
                            section_title,
                            pub_date=edition_date,
                        )
                    )
                    tasks.append(task)
                await asyncio.gather(*tasks)


if __name__ == "__main__":

    class SimpleArgParser(Tap):
        edition_id: int = 7425

    args = SimpleArgParser().parse_args()
    asyncio.run(main(args.edition_id))
