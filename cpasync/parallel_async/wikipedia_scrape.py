import asyncio
import concurrent.futures
import aiofiles
import aiohttp

import time
from math import floor
from multiprocessing import cpu_count

from bs4 import BeautifulSoup
from devtools import debug


async def get_and_scrape_pages(num_pages: int, output_file: str):
    """
    Makes {{num_pages}} requests to Wikipedia to receive {{num_pages}} random
    articles, then scrapes each page for its title and appends it to {{output_file}},
    separating each title with a tab.
    """

    async with aiohttp.ClientSession() as client, aiofiles.open(
        output_file,
        "a+",
        encoding="utf-8",
    ) as f:
        for _ in range(num_pages):
            async with client.get(
                "https://en.wikipedia.org/wiki/Special:Random"
            ) as response:
                if response.status > 399:
                    response.raise_for_status()

                page = await response.text()
                soup = BeautifulSoup(page, features="html.parser")
                title_tag = soup.find("h1")
                if not title_tag:
                    title = "Default title"
                else:
                    title = title_tag.text

                await f.write(title + "\t")
        await f.write("\n")


def start_scraping(num_pages: int, output_file: str, i: int):
    """Start an async process for requesting and scrapig pages"""
    print(f"Process {i} starting...")
    asyncio.run(get_and_scrape_pages(num_pages, output_file))
    print(f"Process {i} finished.")


def main():
    NUM_PAGES = 100
    NUM_CORES = cpu_count() - 1
    OUT_FILE = "./output/tutorials/wikipedia_titles.tsv"

    PAGES_PER_CORE = floor(NUM_PAGES / NUM_CORES)
    PAGES_FOR_LAST_CORE = PAGES_PER_CORE + NUM_PAGES % PAGES_PER_CORE

    futures = []

    with concurrent.futures.ProcessPoolExecutor(NUM_CORES) as executor:
        for i in range(NUM_CORES - 1):
            new_future = executor.submit(
                start_scraping,
                # args to start_scraping, yay
                num_pages=PAGES_PER_CORE,
                output_file=OUT_FILE,
                i=i,
            )
            futures.append(new_future)
        # last core
        futures.append(
            executor.submit(
                start_scraping,
                num_pages=PAGES_FOR_LAST_CORE,
                output_file=OUT_FILE,
                i=NUM_CORES - 1,
            )
        )
    debug(futures)
    concurrent.futures.wait(futures)


if __name__ == "__main__":
    print(f"Starting, please wait....")
    start = time.time()
    main()
    print(f"Time to complete: {round(time.time() - start, 2)} seconds.")
