"""
Downloads contemporanul.ro articles with urls from input/articles-contemporanul.txt

"""
import asyncio
import concurrent.futures
import jsonlines
import aiohttp

from multiprocessing import cpu_count

from typing import List
from bs4 import BeautifulSoup
from random import randint

from devtools import debug
from structlog import get_logger


""" const """
INPUT_URLS = "input/books-urls.txt"
OUTFILE = "output/contemporanul/contemporanul-articles.jsonl"
MAX_NUM_CONNECTIONS = 5
UA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
}

""" globals """
log = get_logger()


async def delay(lo=100, delta=900):
    """Async delay for random miliseconds"""
    await asyncio.sleep(randint(lo, lo + delta) / 1000)


async def scrape_article(
    session: aiohttp.ClientSession,
    url: str,
    writer: jsonlines.Writer,
):
    """Scrape one article from url"""
    log.debug(f"scraping url: {url}")
    await delay()
    async with session.get(url, headers=UA_HEADERS) as resp:
        status = resp.status
        article = {
            "url": url,
            "status": status,
        }
        if status == 200:
            soup = BeautifulSoup(await resp.text(), "lxml")
            title_tag = soup.select_one("h1")
            title = (
                title_tag.getText() if title_tag is not None else "[scrape] No title"
            )
            description_tag = soup.select_one("div#product_description + p")
            description = (
                description_tag.getText()
                if description_tag is not None
                else "[scrape] No description"
            )
            article.update({"title": title, "description": description})

        writer.write(article)
    # -


async def scrape_urls(urls: List[str], writer: jsonlines.Writer):
    """Scrape a list of urls"""
    tasks = []
    connector = aiohttp.TCPConnector(limit_per_host=MAX_NUM_CONNECTIONS)
    async with aiohttp.ClientSession(connector=connector) as session:
        for url in urls:
            task = asyncio.create_task(scrape_article(session, url, writer))
            tasks.append(task)
        await asyncio.gather(*tasks)
    # -


def start_scraping(urls: List[str], process_no: int):
    """Start an async process for scraping a list of urls"""
    # open jsonl writer in this process, append only
    writer = jsonlines.open(OUTFILE, "a")
    log.info(f"Process {process_no} starting with {len(urls)} urls")
    asyncio.run(scrape_urls(urls, writer), debug=True)
    log.info(f"Process {process_no} finished")
    writer.close()


def main():
    # TODO: implement cache to resume downloads
    # wipe outfile
    with open(OUTFILE, "w") as f:
        f.truncate()

    # read urls from input file
    with open(INPUT_URLS, "r") as f:
        # DEBUG
        # urls = f.read().splitlines()
        urls = f.read().splitlines()[:10]
    num_cores = cpu_count() - 1
    chunk_size = int(len(urls) / num_cores) or 1

    futures = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_cores) as executor:
        for i in range(0, len(urls), chunk_size):
            new_future = executor.submit(
                start_scraping,
                urls=urls[i : i + chunk_size],
                process_no=(i // chunk_size),
            )
            futures.append(new_future)
    results = concurrent.futures.wait(futures)
    for result in results.done:
        e = result.exception()
        if e is not None:
            raise e

    log.info("done!")
    # -


if __name__ == "__main__":
    main()
