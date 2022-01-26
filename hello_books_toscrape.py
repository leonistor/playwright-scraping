from playwright.sync_api import sync_playwright
from loguru import logger

import asyncio
import aiohttp


def main():
    url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    with sync_playwright() as pw:
        browser = pw.firefox.launch(headless=True)
        ctx = browser.new_context(
            no_viewport=True,
            accept_downloads=True,
        )
        page = ctx.new_page()
        logger.info(f"Opening URL: {url}")

        page.goto(url)
        page.wait_for_load_state()

        ua = page.evaluate("navigator.userAgent")
        logger.debug(f"agent: {ua}")

        title = page.locator("h1").text_content()
        logger.info(f"title: {title}")

        browser.close()


if __name__ == "__main__":
    main()
