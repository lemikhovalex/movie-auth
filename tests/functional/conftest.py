import asyncio
import os
import sys
from dataclasses import dataclass
from typing import AsyncGenerator, Optional

import aiohttp
import aiopg
import aioredis
import pytest
import pytest_asyncio

from .settings import Settings

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

SETTINGS = Settings()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
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


@pytest_asyncio.fixture(scope="module")
async def redis() -> AsyncGenerator[aiopg.connection.Connection, None]:
    redis_table = aioredis.Redis(host=SETTINGS.redis_host, port=SETTINGS.redis_port)

    yield None

    await redis_table.flushall()


@pytest_asyncio.fixture(scope="module")
async def session(pg_connection, redis):
    session = aiohttp.ClientSession(headers={"Cache-Control": "no-store"})

    yield session

    await session.close()


@dataclass
class HTTPResponse:
    body: dict
    status: int


@pytest_asyncio.fixture(scope="module")
def make_post_request(session):
    """Post request maker"""

    async def inner(
        method: str, json: Optional[dict] = None, headers: Optional[dict] = None
    ) -> HTTPResponse:
        url = f"http://{SETTINGS.api_host}:{SETTINGS.api_port}/api/v1/{method.lstrip('/')}"  # noqa: E501
        async with session.post(url, json=json, headers=headers) as response:
            try:
                body = await response.json()
            except aiohttp.client_exceptions.ContentTypeError:
                body = await response.text()
            return HTTPResponse(
                body=body,
                status=response.status,
            )

    return inner


@pytest_asyncio.fixture(scope="module")
def make_put_request(session):
    """Post request maker"""

    async def inner(
        method: str, json: Optional[dict] = None, headers: Optional[dict] = None
    ) -> HTTPResponse:
        url = f"http://{SETTINGS.api_host}:{SETTINGS.api_port}/api/v1/{method.lstrip('/')}"  # noqa: E501
        async with session.put(url, json=json, headers=headers) as response:
            try:
                body = await response.json()
            except aiohttp.client_exceptions.ContentTypeError:
                body = await response.text()
            return HTTPResponse(
                body=body,
                status=response.status,
            )

    return inner


@pytest_asyncio.fixture(scope="module")
def make_get_request(session):
    """Post request maker"""

    async def inner(
        method: str, json: Optional[dict] = None, headers: Optional[dict] = None
    ) -> HTTPResponse:
        url = f"http://{SETTINGS.api_host}:{SETTINGS.api_port}/api/v1/{method.lstrip('/')}"  # noqa: E501
        async with session.get(url, json=json, headers=headers) as response:
            try:
                body = await response.json()
            except aiohttp.client_exceptions.ContentTypeError:
                body = await response.text()
            return HTTPResponse(
                body=body,
                status=response.status,
            )

    return inner


@pytest_asyncio.fixture(scope="module")
def make_delete_request(session):
    """Post request maker"""

    async def inner(
        method: str, json: Optional[dict] = None, headers: Optional[dict] = None
    ) -> HTTPResponse:
        url = f"http://{SETTINGS.api_host}:{SETTINGS.api_port}/api/v1/{method.lstrip('/')}"  # noqa: E501
        async with session.delete(url, json=json, headers=headers) as response:
            try:
                body = await response.json()
            except aiohttp.client_exceptions.ContentTypeError:
                body = await response.text()
            return HTTPResponse(
                body=body,
                status=response.status,
            )

    return inner


@pytest_asyncio.fixture(scope="module")
async def access_token(make_post_request):
    response = await make_post_request(
        "auth/login",
        json={"login": "test1", "password": "test1"},
        headers={"User-Agent": "agent_1"},
    )

    yield response.body["access_token"]


@pytest_asyncio.fixture(scope="module")
async def second_access_token(make_post_request):
    response = await make_post_request(
        "auth/login",
        json={"login": "test1", "password": "test1"},
        headers={"User-Agent": "agent_2"},
    )

    yield response.body["access_token"]


@pytest_asyncio.fixture(scope="module")
async def third_access_token(make_post_request):
    response = await make_post_request(
        "auth/login",
        json={"login": "test1", "password": "test1"},
        headers={"User-Agent": "agent_2"},
    )

    yield response.body["access_token"]
