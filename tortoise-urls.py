"""
Try tortoise-orm for the url cache.
"""

import asyncio
from faker import Faker

from tortoise import Tortoise, fields
from tortoise.models import Model
from enum import Enum

DB = "sqlite://db/tortoise-urls.sqlite"


class Status(Enum):
    NEW = "NEW"
    ERR = "ERR"
    OKK = "OKK"


class Url(Model):
    url = fields.CharField(pk=True, unique=True, max_length=255 * 4)
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

    print(await Url.all())

    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
