"""
Downloads contemporanul.ro articles with urls from input/articles-contemporanul.txt


"""
import asyncio
import concurrent.futures
import aiofiles
import aiohttp

from multiprocessing import cpu_count

from typing import List
from bs4 import BeautifulSoup
from random import randint
from devtools import debug

""" const """
INPUT_URLS = "input/books-urls.txt"


async def delay(lo=100, hi=900):
    await asyncio.sleep(randint(lo, hi) / 1000)


async def scrape_urls(urls: List[str]):
    """Scrape a list of urls"""
    for url in urls:
        print(f"scraping {url}")
        # await delay(lo=3000, hi=4000)
        await delay()


def start_scraping(urls: List[str], process_no: int):
    """Start an async process for scraping a list of urls"""
    print(f"Process {process_no} starting...")
    asyncio.run(scrape_urls(urls))
    print(f"Process {process_no} finished")


def main():
    with open(INPUT_URLS, "r") as f:
        urls = f.read().splitlines()
    num_cores = cpu_count() - 1
    chunk_size = int(len(urls) / num_cores) or 1

    futures = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_cores) as executor:
        for i in range(0, len(urls), chunk_size):
            debug(urls[i : i + chunk_size])
            new_future = executor.submit(
                start_scraping,
                urls[i : i + chunk_size],
                i // chunk_size,
            )
            futures.append(new_future)
    concurrent.futures.wait(futures)


if __name__ == "__main__":
    main()
