from dataclasses import dataclass

import aiohttp
import pytest
from multidict import CIMultiDictProxy
from settings import TestSettings

# All test coroutines will be treated as marked with this decorator.
pytestmark = pytest.mark.asyncio
SETTINGS = TestSettings()


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


async def test_login_logout_check(session: aiohttp.ClientSession):

    # create user
    url = f"http://{SETTINGS.api_host}:{SETTINGS.api_port}/api/v1/users/"  # noqa: E501
    data = {
        "credentials": {"login": "test1", "password": "test1"},
        "user_data": {"first_name": "13", "second_name": "Est"},
    }
    async with session.post(url, json=data) as response:
        resp = HTTPResponse(
            body=await response.json(),
            headers=response.headers,
            status=response.status,
        )
        assert resp.status == 201

    # login
    url = f"http://{SETTINGS.api_host}:{SETTINGS.api_port}/api/v1/auth/login"  # noqa: E501
    data = {"login": "test1", "password": "test1"}
    async with session.post(url, json=data) as response:
        resp = HTTPResponse(
            body=await response.json(),
            headers=response.headers,
            status=response.status,
        )
        assert resp.status == 200
        auth_token = resp.body["access_token"]

    # check access
    url = f"http://{SETTINGS.api_host}:{SETTINGS.api_port}/api/v1/auth/check"  # noqa: E501
    async with session.post(url, headers={"Authorization": auth_token}) as response:
        resp = HTTPResponse(
            body=await response.json(),
            headers=response.headers,
            status=response.status,
        )
        assert resp.status == 200

    # log out
    url = f"http://{SETTINGS.api_host}:{SETTINGS.api_port}/api/v1/auth/logout"  # noqa: E501
    async with session.post(url, headers={"Authorization": auth_token}) as response:
        resp = HTTPResponse(
            body={},
            headers=response.headers,
            status=response.status,
        )
        assert resp.status == 200

    # check access
    url = f"http://{SETTINGS.api_host}:{SETTINGS.api_port}/api/v1/auth/check"  # noqa: E501
    async with session.post(url, headers={"Authorization": auth_token}) as response:
        assert response.status == 403
