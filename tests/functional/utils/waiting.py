import asyncio
import logging

import aiopg
from aioredis import Redis
from psycopg2 import OperationalError
from settings import Settings

logger = logging.getLogger(__name__)
SETTINGS = Settings()


async def wait_for_pg():
    timeout = 0

    is_done = False
    while not is_done and timeout < SETTINGS.service_wait_timeout:
        try:
            conn = await aiopg.connect(
                host=SETTINGS.pg_host,
                database=SETTINGS.pg_db,
                user=SETTINGS.pg_user,
                password=SETTINGS.pg_password,
            )
            is_done = True
            await conn.close()
        except OperationalError:
            timeout += SETTINGS.service_wait_interval


async def wait_for_redis():
    redis = Redis(host=SETTINGS.redis_host, port=SETTINGS.redis_port)
    timeout = 0
    while not (await redis.ping()) and timeout < SETTINGS.service_wait_timeout:
        await asyncio.sleep(SETTINGS.service_wait_interval)
        timeout += SETTINGS.service_wait_interval
    await redis.close()
