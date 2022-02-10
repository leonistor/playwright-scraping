"""
testing aiosqlite with aiosql (run SQL queries defined in strings/files)
"""

import asyncio
import aiosqlite
import aiosql

from faker import Faker

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

-- name: upsert_url!
-- Insert or replace an url
INSERT OR REPLACE INTO urls(url, status) VALUES(:url, :status);

-- name: bulk_insert_urls*!
-- Bulk insert (*!) a list of urls
INSERT INTO urls(url, status)
VALUES(:url, :status);

-- name: get_urls
SELECT url, status FROM urls;

-- name: get_urls_by_status
SELECT url, status FROM urls WHERE status = :status;
"""

query = aiosql.from_str(SQL, "aiosqlite")


async def create_tables(conn: aiosqlite.Connection):
    pass


async def create_dummy_urls(conn: aiosqlite.Connection):
    fkr = Faker()
    statuses = ["new", "error", "done"]
    urls = [
        {
            "url": fkr.unique.url(),
            "status": fkr.random_elements(elements=statuses)[0],
        }
        for _ in range(100)
    ]
    await query.bulk_insert_urls(conn, urls)
    await conn.commit()


async def show_urls(conn: aiosqlite.Connection):
    urls = await query.get_urls(conn)
    debug(urls[:10])


async def main():
    async with aiosqlite.connect(DB) as conn:
        # await create_dummy_urls(conn)
        print("--- before")
        await show_urls(conn)
        doned = [
            "https://www.leon.net/",
            "https://www.gregory.org/",
            "http://guerrero.com/",
            "http://alvarez.com/",
        ]
        for url in doned:
            await query.upsert_url(conn, url=url, status="done")
            await conn.commit()
        print("--- after")
        await show_urls(conn)


asyncio.run(main())
