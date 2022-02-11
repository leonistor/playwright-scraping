"""
Try tortoise-orm for the url cache.
"""

import asyncio

from tortoise import Tortoise, fields
from tortoise.models import Model
from enum import Enum

from devtools import debug

DB = "sqlite://db/tortoise-urls.sqlite"


class Status(Enum):
    NEW = "NEW"
    ERR = "ERR"
    OKK = "OKK"


class Url(Model):
    url = fields.CharField(pk=True, unique=True, max_length=255 * 8)
    status = fields.CharEnumField(
        Status,
        default=Status.NEW,
    )

    class Meta:
        table = "urls"

    def __str__(self):
        return f"[{self.status}] {self.url[:20]}"


async def main():
    await Tortoise.init(
        db_url=DB,
        modules={"models": ["__main__"]},
    )
    await Tortoise.generate_schemas()

    urls = [
        Url(url="url1"),
        Url(url="url2"),
        Url(url="url3"),
    ]
    await Url.bulk_create(urls)

    zashit = await Url.all().values()
    debug(zashit)

    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
