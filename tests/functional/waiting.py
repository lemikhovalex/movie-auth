import asyncio

from utils.waiting import wait_for_pg, wait_for_redis


async def main():
    await asyncio.gather(wait_for_pg(), wait_for_redis())


if __name__ == "__main__":
    asyncio.run(main())
