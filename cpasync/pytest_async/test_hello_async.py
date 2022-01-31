import pytest

from hello_async import say_hello


@pytest.mark.parametrize(
    "name",
    [
        "Coca Shefa",
        "Baba cu cireshe in gaoaza",
        "x Æ a-12",
    ],
)
@pytest.mark.asyncio
async def test_say_hello(name):
    await say_hello(name)
