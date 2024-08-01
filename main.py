import asyncio
from bot_init import start_bot
from logging_setup import setup_logging

setup_logging()


async def main():
    await asyncio.gather(
        start_bot()
    )

if __name__ == '__main__':
    asyncio.run(main())
