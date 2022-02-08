"""
Download articles urls from categories pages of mytex.ro
"""
from playwright.sync_api import sync_playwright, Page


from random import randint
from structlog import get_logger
from devtools import debug

""" globals """
log = get_logger()


def delay(page: Page):
    page.wait_for_timeout(randint(100, 900))


def main():
    url = "https://www.mytex.ro/economic.html#p3"
    with sync_playwright() as pw:
        browser = pw.firefox.launch(
            headless=False,
            proxy={
                "server": "http://intelnuc:3129",
            },
        )
        ctx = browser.new_context(
            no_viewport=True,
            accept_downloads=True,
        )
        page = ctx.new_page()

        page.goto(url)
        page.wait_for_load_state()

        log.info(f"url: {page.url}")
        try:
            category = page.locator("h3#aiMyTexSearchHeaderMain").text_content()
            log.info(f"category: {category}")
        except TimeoutError as e:
            log.error("fuck")
            raise e

        delay(page)
        footer = page.locator(".customfooter")
        footer.scroll_into_view_if_needed(timeout=0)
        log.info("footer scrolled")
        delay(page)

        # get articles urls
        articles = page.locator("li.liAiMyTexSearchItem a.a_aiMyTexSearchItemTitle")
        articles_urls = articles.evaluate_all("list => list.map(e => e.href)")
        log.info(f"getting articles!")
        debug(articles_urls)
        page.wait_for_timeout(3000)

        try:
            more_btn = page.locator("input#btnAiMyTexSearchLoadMore")
            more_btn.scroll_into_view_if_needed()
            log.debug("clicked for more")
            page.click("input#btnAiMyTexSearchLoadMore")
            page.wait_for_timeout(3000)
        except TimeoutError as e:
            log.error("fuck")
            raise e
        log.info(f"url: {page.url}")

        try:
            next_page = page.locator("li.pagination-next a.pagenav")
            next_page.scroll_into_view_if_needed()
            log.debug("click next page")
            page.click("li.pagination-next a.pagenav")
            page.wait_for_timeout(3000)
        except TimeoutError as e:
            log.error("fuck")
            raise e
        log.info(f"url: {page.url}")

        page.wait_for_timeout(3000)
        browser.close()


if __name__ == "__main__":
    main()
