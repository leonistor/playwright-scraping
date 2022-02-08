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
""" globals """
log = get_logger()


def delay(page: Page):
    page.wait_for_timeout(randint(100, 900))


def save_articles_urls(page: Page, f: TextIOWrapper):
    # get articles urls
    articles = page.locator("li.liAiMyTexSearchItem a.a_aiMyTexSearchItemTitle")
    articles_urls = articles.evaluate_all("list => list.map(e => e.href)")
    f.write("\n".join(articles_urls))
    log.info(f"saved {len(articles_urls)} urls from {page.url}")


def main():
    # read categories start pages from file:
    with open(CATEGORIES_FILES, "r") as f:
        categories = f.read().splitlines()
    # reset output file
    fout = open(OUTFILE, "w")
    fout.truncate()

    url = "https://www.mytex.ro/politic.html#p3"
    with sync_playwright() as pw:
        # prepare playwright
        browser = pw.firefox.launch(
            headless=True,
            proxy={
                "server": "http://intelnuc:3129",
            },
        )
        ctx = browser.new_context(
            no_viewport=True,
            accept_downloads=True,
        )
        ctx.set_default_timeout(60 * 1000)
        page = ctx.new_page()

        # category start page
        page.goto(url)
        page.wait_for_load_state()

        # scroll to bottom
        delay(page)
        footer = page.locator(".customfooter")
        footer.scroll_into_view_if_needed(timeout=0)
        delay(page)
        save_articles_urls(page, fout)

        # category second page: from 'Mai multe...' button
        try:
            more_btn = page.locator("input#btnAiMyTexSearchLoadMore")
            more_btn.scroll_into_view_if_needed()
            page.click("input#btnAiMyTexSearchLoadMore")
            page.wait_for_load_state()
            save_articles_urls(page, fout)
        except TimeoutError as e:
            log.error(f"url: {page.url}, error: {e}")
            raise e

        # rest of page: click on bottom pagination '>'
        for _ in range(10):
            try:
                next_page_arrow = page.locator("li.pagination-next a.pagenav")
                next_page_arrow.scroll_into_view_if_needed()
                page.click("li.pagination-next a.pagenav")
                page.wait_for_load_state()
                save_articles_urls(page, fout)
            except TimeoutError as e:
                log.error(f"url: {page.url}, error: {e}")
                raise e

        browser.close()

    # cleanup
    fout.close()

    # -


if __name__ == "__main__":
    main()
