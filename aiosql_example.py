"""
testing aiosqlite with aiosql (run SQL queries defined in strings/files)
"""

import asyncio
import aiosqlite
import aiosql

from devtools import debug


DB = "db/example.sqlite"
SQL = """
-- name: create_tables
CREATE TABLE IF NOT EXISTS urls (
        url    TEXT NOT NULL UNIQUE PRIMARY KEY,
        status TEXT NOT NULL
);

-- name: insert_url!
-- Insert an url without returning any result (!)
INSERT INTO urls(url, status) VALUES(:url, :status);

-- name: get_urls
SELECT url, status FROM urls;

-- name: get_urls_by_status
SELECT url, status FROM urls WHERE status = :status;
"""

query = aiosql.from_str(SQL, "aiosqlite")


async def create_tables(conn: aiosqlite.Connection):
    pass


async def create_dummy_urls(conn: aiosqlite.Connection):
    await query.insert_url(conn, url="https://anaaremere.com", status="done")


async def show_urls(conn: aiosqlite.Connection):
    urls = await query.get_urls(conn)
    debug(urls)


async def main():
    async with aiosqlite.connect(DB) as conn:
        await create_dummy_urls(conn)
        await show_urls(conn)


asyncio.run(main())
