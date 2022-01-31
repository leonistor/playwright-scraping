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


class TestSayHelloThrowsExcptions:
    @pytest.mark.parametrize(
        "name",
        [
            "",
        ],
    )
    @pytest.mark.asyncio
    async def test_say_hello_value_error(self, name):
        with pytest.raises(ValueError):
            await say_hello(name)

    @pytest.mark.parametrize(
        "name",
        [
            19,
            {"ana": "mere"},
            [],
        ],
    )
    @pytest.mark.asyncio
    async def test_say_hello_type_error(self, name):
        with pytest.raises(TypeError):
            await say_hello(name)
