import asyncio
import os
import sys
from dataclasses import dataclass
from typing import AsyncGenerator

import aiohttp
import aiopg
import pytest
import pytest_asyncio
from multidict import CIMultiDictProxy

from .settings import TestSettings

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

SETTINGS = TestSettings()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def pg_connection() -> AsyncGenerator[aiopg.connection.Connection, None]:
    os.system("python3 main_build_tables.py")
    dsn = "dbname={dbname} user={user} password={password} host={host}".format(
        dbname=SETTINGS.pg_db,
        user=SETTINGS.pg_user,
        password=SETTINGS.pg_password,
        host=SETTINGS.pg_host,
    )
    async with aiopg.create_pool(dsn) as pool:
        async with pool.acquire() as conn:

            yield conn

            async with conn.cursor() as cur:
                await cur.execute("TRUNCATE users CASCADE;")
                await cur.execute("TRUNCATE user_data CASCADE;")
                await cur.execute("TRUNCATE sessions CASCADE;")
                await cur.execute("TRUNCATE users_roles CASCADE;")


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest_asyncio.fixture(scope="session")
async def session(pg_connection):  # use es_client arg to call index creation fixture
    session = aiohttp.ClientSession(headers={"Cache-Control": "no-store"})

    yield session

    await session.close()
