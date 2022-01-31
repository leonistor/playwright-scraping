import asyncio


async def say_hello(name: str):
    """Sleeps for one second, then prints 'Hello, <name>'"""
    try:
        if type(name) != str:
            raise TypeError("'name' must be a string")
        if name == "":
            raise ValueError("'name' cannot be ampty")
    except (TypeError, ValueError):
        raise

    print("Sleeping...")
    await asyncio.sleep(1)
    print(f"Hello, {name}")
