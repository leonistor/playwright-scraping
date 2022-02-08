"""
Download articles urls from categories pages of mytex.ro
"""
from io import TextIOWrapper
from playwright.sync_api import sync_playwright, Page

from random import randint
from structlog import get_logger
from devtools import debug

""" const """
OUTFILE = "input/articles-mytex.txt"
CATEGORIES_FILES = "input/categories-mytex.txt"
CURRENT_CATEGORY = 18
CONTEXT_TIMEOUT = 1000 * 90
""" globals """
log = get_logger()


def delay(page: Page):
    page.wait_for_timeout(randint(100, 900))


def save_articles_urls(page: Page, f: TextIOWrapper):
    # get articles urls
    articles = page.locator("li.liAiMyTexSearchItem a.a_aiMyTexSearchItemTitle")
    articles_urls = articles.evaluate_all("list => list.map(e => e.href)")
    f.write("\n".join(articles_urls) + "\n")
    log.info(f"saved {len(articles_urls)} urls from {page.url}")


def main():
    # read categories start pages from file:
    with open(CATEGORIES_FILES, "r") as f:
        categories = f.read().splitlines()

    with sync_playwright() as pw, open(OUTFILE, "w") as fout:
        # prepare playwright
        browser = pw.firefox.launch(
            headless=True,
            # slow_mo=3,
            proxy={
                "server": "http://intelnuc:3129",
            },
        )
        ctx = browser.new_context(
            no_viewport=True,
            accept_downloads=True,
        )
        ctx.set_default_timeout(CONTEXT_TIMEOUT)
        page = ctx.new_page()

        for url in categories:
            log.info(f"PROCESSING CATEG {url}")
            # category start page
            page.goto(url)
            page.wait_for_load_state(state="domcontentloaded")

            # scroll to bottom
            delay(page)
            footer = page.locator(".customfooter")
            footer.scroll_into_view_if_needed(timeout=0)
            more_btn = page.locator("input#btnAiMyTexSearchLoadMore")
            more_btn.wait_for(state="attached")
            save_articles_urls(page, fout)

            # category second page: from 'Mai multe...' button
            try:
                more_btn.scroll_into_view_if_needed()
                delay(page)
                page.click("input#btnAiMyTexSearchLoadMore")
                page.wait_for_load_state(state="domcontentloaded")
                save_articles_urls(page, fout)
            except Exception as e:
                log.error(f"url: {page.url}, error: {e}")
                raise e

            # rest of page: click on bottom pagination '>'
            has_next_page = True
            page_count = 3
            # for _ in range(10):
            while has_next_page:
                try:
                    delay(page)
                    next_page_arrow = page.locator("li.pagination-next a.pagenav")
                    next_page_arrow.scroll_into_view_if_needed()
                    page.click("li.pagination-next a.pagenav")
                    page.wait_for_load_state(state="domcontentloaded")
                    save_articles_urls(page, fout)
                    page_count += 1
                except Exception as e:
                    has_next_page = False
                    log.error(f"url: {page.url}, error: {e}")
                    log.info(f"done at page {page_count}")
                    # raise e
                    pass
        # - for categories

        browser.close()
        # - sync_playwright, fout

    # -


if __name__ == "__main__":
    main()
