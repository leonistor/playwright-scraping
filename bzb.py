import asyncio
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


async def save_image(session, outdir: str, image_url: str, image_file: str):
    async with session.get(image_url, headers=UA_HEADERS) as resp:
        log.debug("image", url=image_url, file=image_file, status=resp.status)
        if resp.status == 200:
            fimg = await aiofiles.open(f"{outdir}/{image_file}", "wb")
            await fimg.write(await resp.read())
            await fimg.close()


async def get_article(
    url: str,
    session: aiohttp.ClientSession,
    section_title: str,
    pub_date: str,
    outdir: str,
    writer: Writer,
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
            text_tag = soup.select_one(".txt_articol > p:nth-child(2)")
            if text_tag is not None:
                text = str(text_tag)
            else:
                text = ""
            article["text"] = text
            # article image
            img = soup.select_one(".article_img")
            if (img is not None) and img.has_attr("src"):
                src = str(img["src"])
                img_file = src.split("/")[-1]
                img_url = f"{BASE_URL}{src}"
                article["img"] = img_file
                await save_image(
                    session,
                    outdir,
                    image_url=img_url,
                    image_file=img_file,
                )

        else:
            # oops
            article["error"] = resp.status
    # log.debug("article", article=article)
    writer.write(article)


async def main(edition_id: int, outdir: str, writer: Writer):
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
                            outdir=outdir,
                            writer=writer,
                        )
                    )
                    tasks.append(task)
                await asyncio.gather(*tasks)


if __name__ == "__main__":

    class SimpleArgParser(Tap):
        edition_id: int = 7425

    args = SimpleArgParser().parse_args()

    outdir = f"output/bzb/{args.edition_id}"
    os.makedirs(outdir, exist_ok=True)
    fout = open(outdir + f"/articles-bzb-{args.edition_id}.jsonl", "w")
    writer = Writer(fout)
    asyncio.run(
        main(
            edition_id=args.edition_id,
            outdir=outdir,
            writer=writer,
        )
    )
