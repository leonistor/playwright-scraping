"""
Downloads mytex.ro articles with urls from input file.
"""
import asyncio
import concurrent.futures
from weakref import proxy
import jsonlines

import aiohttp
import aiohttp_client_cache.session

from multiprocessing import cpu_count

from typing import List
from bs4 import BeautifulSoup
from random import randint

from devtools import debug
import logging


""" const """
# INPUT_URLS = "input/articles-mytex.txt"
INPUT_URLS = "input/articles-mytex-small.txt"
OUTFILE = "output/mytex/articles-mytex.jsonl"
MAX_NUM_CONNECTIONS = 5
MAX_TIMEOUT = 2000
UA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
}

""" globals """
logging.basicConfig(
    format="▸ %(asctime)s.%(msecs)03d %(filename)s:%(lineno)d %(levelname)s %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
)


async def delay(lo=100, delta=900):
    """Async delay for random miliseconds"""
    await asyncio.sleep(randint(lo, lo + delta) / 1000)


def parse_article(soup: BeautifulSoup):
    """Parse HTML of a single article into a dict."""
    article = {}
    category_tag = soup.select_one("#mytex_middle_content_component_div1 h3")
    category = (
        category_tag.get_text() if category_tag is not None else "[scrape] no category"
    )
    title_tag = soup.select_one("h2.contentheading")
    title = title_tag.get_text() if title_tag is not None else "[scrape] no title"
    # article text
    content_tag = soup.select(".item-page p:not([class])")
    if content_tag is not None:
        content = [p.get_text() for p in content_tag]
    else:
        content = "[scrape] No content"
    author_tag = soup.select_one("dl.article-info dd.createdby")
    author = author_tag.get_text() if author_tag is not None else "[scrape] no author"
    published_tag = soup.select_one("dl.article-info dd.published")
    published = (
        published_tag.get_text() if published_tag is not None else "[scrape] no author"
    )
    # image?

    article.update(
        {
            "title": title,
            "content": content,
            "category": category,
            "author": author,
            "published": published,
        }
    )
    return article


async def scrape_article(
    session: aiohttp.ClientSession,
    url: str,
    writer: jsonlines.Writer,
):
    """Scrape one article from url"""
    await delay()

    async with session.get(
        url,
        headers=UA_HEADERS,
        proxy="http://intelnuc:3129",
    ) as resp:
        status = resp.status
        article = {
            "url": url,
            "status": status,
        }
        if status == 200:
            soup = BeautifulSoup(await resp.text(), "lxml")
            article_data = parse_article(soup)
            article.update(**article_data)
        else:
            logging.error(f"article: status: {status}, url:{url}")

        writer.write(article)

    return {"status": status, "url": url}
    # -


# https://quantlane.com/blog/ensure-asyncio-task-exceptions-get-logged/
def _handle_task_result(task: asyncio.Task) -> None:
    try:
        task.result()
    except asyncio.CancelledError:
        pass  # this is ok
    except Exception:
        logging.exception("Exception raised by task = %r", task)


async def scrape_urls(urls: List[str], writer: jsonlines.Writer):
    """Scrape a list of urls"""
    tasks = []
    connector = aiohttp.TCPConnector(limit_per_host=MAX_NUM_CONNECTIONS)
    timeout = aiohttp.ClientTimeout(total=MAX_TIMEOUT)
    async with aiohttp_client_cache.session.CachedSession(
        connector=connector,
        timeout=timeout,
    ) as session:
        for url in urls:
            task = asyncio.create_task(scrape_article(session, url, writer))
            task.add_done_callback(_handle_task_result)
            tasks.append(task)
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            print(repr(e))
    # -


def start_scraping(urls: List[str], process_no: int):
    """Start an async process for scraping a list of urls"""
    # open jsonl writer in this process, append only
    writer = jsonlines.open(OUTFILE, "a")
    logging.info(f"Process {process_no} starting with {len(urls)} urls")
    asyncio.run(scrape_urls(urls, writer))
    logging.info(f"Process {process_no} finished")
    writer.close()


def main():
    # wipe outfile
    with open(OUTFILE, "w") as f:
        f.truncate()

    # read urls from input file
    with open(INPUT_URLS, "r") as f:
        urls = f.read().splitlines()

    # split urls into num_cores chunks
    num_cores = cpu_count() - 1
    chunk_size = int(len(urls) / num_cores) or 1

    logging.info(f"num urls: {len(urls)}")

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

    logging.info("done!")
    # -


if __name__ == "__main__":
    main()