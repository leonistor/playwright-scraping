"""
Downloads bizbrasov.ro articles with urls from input file.
"""
import asyncio
import aiofiles
import concurrent.futures
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
INPUT_URLS = "input/articles-bizbrasov.txt"
OUTFILE = "output/bizbrasov/articles-bizbrasov.jsonl"
OUTDIR = "output/bizbrasov/img/"
MAX_NUM_CONNECTIONS = 5
MAX_TIMEOUT = 9000
UA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
}

""" globals """
logging.basicConfig(
    format="▸ %(levelname)s %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
)


async def delay(lo=100, delta=900):
    """Async delay for random miliseconds"""
    await asyncio.sleep(randint(lo, lo + delta) / 1000)


async def save_image(session, outdir: str, image_url: str, image_file: str):
    await delay()
    async with session.get(
        image_url,
        headers=UA_HEADERS,
        proxy="http://intelnuc:3129",
    ) as resp:
        # log.debug("image", url=image_url, file=image_file, status=resp.status)
        if resp.status == 200:
            fimg = await aiofiles.open(f"{outdir}{image_file}", "wb")
            await fimg.write(await resp.read())
            await fimg.close()


def parse_article(soup: BeautifulSoup):
    """Parse HTML of a single article into a dict."""
    article = {}
    category_tag = soup.select_one(".the-post-meta span.cats a:last-child")
    category = (
        category_tag.get_text() if category_tag is not None else "[scrape] no category"
    )
    title_tag = soup.select_one("h1.post-title")
    title = title_tag.get_text() if title_tag is not None else "[scrape] no title"
    # article text
    content_tag = soup.select(".post-content > *:is(h2,p)")
    if content_tag is not None:
        content = [t.get_text() for t in content_tag]
    else:
        content = "[scrape] No content"
    author_tag = soup.select_one("span.posted-by span.reviewer")
    author = author_tag.get_text() if author_tag is not None else "[scrape] no author"
    published_tag = soup.select_one("span.posted-on time")
    published = (
        published_tag.get_text()
        if published_tag is not None
        else "[scrape] no published date"
    )
    image_url, image_file = "", ""
    image_tag = soup.select_one("figure.wp-block-image img")
    if image_tag:
        image_url = image_tag.get("src")
        if isinstance(image_url, str):
            # https://www.bizbrasov.ro/wp-content/uploads/2020/05/comisia-europeana.hmoju2sqv5-2-1024x768.jpg
            image_file = "_".join(image_url.split("/")[5:])

    article.update(
        {
            "title": title.strip(),
            "content": content,
            "category": category.strip().lower(),
            "author": author,
            "published": published.strip(),
            "image_url": image_url,
            "image_file": image_file,
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
        if article["image_url"]:
            await save_image(
                session=session,
                outdir=OUTDIR,
                image_url=article["image_url"],
                image_file=article["image_file"],
            )

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
