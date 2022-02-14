"""
Try handling infinite scroll with playwright
"""

from playwright.sync_api import sync_playwright, Page

from random import randint

# from devtools import debug
import logging


""" const """
OUTFILE = "input/articles-pressone.txt"
CATEGORIES_FILES = "input/categories-pressone.txt"

CONTEXT_TIMEOUT = 1000 * 90


""" globals """
logging.basicConfig(
    format="▸ %(levelname)s %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
)


def delay(page: Page):
    page.wait_for_timeout(randint(100, 900))


def main():
    with open(CATEGORIES_FILES, "r") as f:
        categories = f.read().splitlines()

    with sync_playwright() as pw, open(OUTFILE, "w") as fout:
        # prepare playwright
        browser = pw.firefox.launch(
            headless=False,
            slow_mo=10,
            # proxy={
            #     "server": "http://intelnuc:3129",
            # },
        )
        ctx = browser.new_context(
            no_viewport=True,
            accept_downloads=True,
        )
        ctx.set_default_timeout(CONTEXT_TIMEOUT)
        page = ctx.new_page()

        for url in categories:
            page.goto(url)
            logging.debug(f"visiting {url}")
            page.wait_for_load_state(state="domcontentloaded")

            # scroll to bottom
            last_height = page.evaluate("() => document.body.scrollHeight")
            while True:
                page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_load_state(state="domcontentloaded")
                logging.debug("scroll!")
                delay(page)
                new_height = page.evaluate("() => document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            # while True
            logging.debug("scroll ended!")
            page.wait_for_timeout(2 * 1000)
            articles = page.locator("a.jWrOUT")
            articles_urls = articles.evaluate_all("list => list.map(e => e.href)")
            fout.write("\n".join(articles_urls) + "\n")
            logging.debug(f"collected {len(articles_urls)}")
        # - for url categories

        browser.close()
        # - sync_playwright, fout
        logging.debug("done!")
    # -


if __name__ == "__main__":
    main()
