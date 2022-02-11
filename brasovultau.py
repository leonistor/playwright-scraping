"""
Download list of articles urls from www.brasovultau.ro
to be scraped later by brasovultau_download.py
"""

from io import TextIOWrapper
from playwright.sync_api import sync_playwright, Page

from random import randint

# DEBUG
from devtools import debug
import logging


""" const """
OUTFILE = "input/articles-brasovultau.txt"
CATEGORIES_FILES = "input/categories-brasovultau.txt"
CONTEXT_TIMEOUT = 1000 * 90
UA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
}

""" globals """
logging.basicConfig(
    format="▸ :%(lineno)d %(levelname)s %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
)
logging.debug("started")


def delay(page: Page):
    page.wait_for_timeout(randint(100, 900))


def save_articles_urls(page: Page, f: TextIOWrapper):
    # get articles urls
    articles = page.locator(".item .item-title a")
    articles_urls = articles.evaluate_all("list => list.map(e => e.href)")
    f.write("\n".join(articles_urls) + "\n")
    logging.info(f"saved {len(articles_urls)} urls from {page.url}")


def main():
    # read categories start pages from file:
    with open(CATEGORIES_FILES, "r") as f:
        categories = f.read().splitlines()

    with sync_playwright() as pw, open(OUTFILE, "w") as fout:
        # prepare playwright
        # DEBUG
        browser = pw.firefox.launch(
            headless=False,
            # DEBUG
            slow_mo=3,
        )
        ctx = browser.new_context(
            no_viewport=True,
            accept_downloads=True,
        )
        ctx.set_default_timeout(CONTEXT_TIMEOUT)
        page = ctx.new_page()

        # DEBUG
        for url in categories[:3]:
            logging.info(f"PROCESSING CATEG {url}")
            # category start page
            page.goto(url)
            page.wait_for_load_state(state="domcontentloaded")
            save_articles_urls(page, fout)

            # rest of page: click on pagination '>'
            has_next_page = True
            page_count = 1
            # DEBUG
            while has_next_page and page_count < 5:
                try:
                    delay(page)
                    next_page_arrow = page.locator("a.pageNo.nextPage").first
                    next_page_arrow.click()
                    page.wait_for_load_state(state="domcontentloaded")
                    save_articles_urls(page, fout)
                    page_count += 1
                except Exception as e:
                    has_next_page = False
                    # logging.error(f"url: {page.url}, error: {e}")
                    logging.info(f"done at page {page_count}")
                    # raise e
                    pass
                    # raise e
            # - while has_next_page
        # - for categories
        browser.close()
    # - sync_playwright, fout
    logging.debug("done")
    # -


if __name__ == "__main__":
    main()
