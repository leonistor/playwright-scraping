import asyncio
import aiohttp
import aiofiles
import os

from structlog import get_logger
from tap import Tap
from jsonlines import Writer

from bs4 import BeautifulSoup
from bs4.element import Tag

""" const """
MAX_NUM_CONNECTIONS = 5
BASE_URL = "https://www.contemporanul.ro/numere/"
UA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
}


""" globals """
log = get_logger()


async def main(an: int, outdir: str):
    luni = []
    for i in range(1, 13):
        luni.append("{:02d}".format(i))
    # TODO: fout si writer pe luni
    fout = open(outdir + f"/articles-contemporanul-{an}.jsonl", "w")
    writer = Writer(fout)


if __name__ == "__main__":

    class SimpleArgParser(Tap):
        an: int = 2014

    args = SimpleArgParser().parse_args()
    outdir = f"output/contemporanul/{args.an}"
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(f"{outdir}/img", exist_ok=True)

    asyncio.run(main(an=args.an, outdir=outdir))
