import asyncio
from random import randint


async def delay(lo=100, hi=900):
    await asyncio.sleep(randint(lo, hi) / 1000)


async def main():
    for i in range(10):
        print(i)
        await delay()


asyncio.run(main())
