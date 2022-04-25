import time
from http import HTTPStatus

import pytest

# All test coroutines will be treated as marked with this decorator.
pytestmark = pytest.mark.asyncio


async def test_user_create(make_request):
    response = await make_request("post")(
        "users",
        json={
            "credentials": {"login": "test1", "password": "test1"},
            "user_data": {"first_name": "13", "second_name": "Est"},
        },
    )

    assert response.status == HTTPStatus.CREATED


async def test_login(make_request):
    response = await make_request("post")(
        "auth/login",
        json={"login": "test1", "password": "test1"},
    )

    assert response.status == HTTPStatus.OK


async def test_check_authorized(make_request, access_token):
    response = await make_request("post")(
        "auth/check",
        headers={"Authorization": access_token},
    )

    assert response.status == HTTPStatus.OK


async def test_logout_all(make_request, access_token):
    time.sleep(1)
    response = await make_request("post")(
        "auth/logout_all",
        headers={"Authorization": access_token},
    )
    assert response.status == HTTPStatus.OK


async def test_check_notauthorized_first_agent(make_request, access_token):
    response = await make_request("post")(
        "auth/check",
        headers={"Authorization": access_token, "User-Agent": "agent_1"},
    )

    assert response.status == HTTPStatus.FORBIDDEN


async def test_check_notauthorized_second_agent(make_request, second_access_token):
    response = await make_request("post")(
        "auth/check",
        headers={"Authorization": second_access_token, "User-Agent": "agent_2"},
    )

    assert response.status == HTTPStatus.FORBIDDEN


async def test_log_in_first(make_request, access_token):
    time.sleep(1)
    response = await make_request("post")(
        "auth/login",
        json={"login": "test1", "password": "test1"},
        headers={"User-Agent": "agent_1"},
    )

    assert response.status == HTTPStatus.OK


async def test_check_after_first_logged_in(make_request, third_access_token):
    response = await make_request("post")(
        "auth/check",
        headers={"Authorization": third_access_token, "User-Agent": "agent_1"},
    )

    assert response.status == HTTPStatus.OK


async def test_check_socend_after_first_logged_in(make_request, second_access_token):
    response = await make_request("post")(
        "auth/check",
        headers={"Authorization": second_access_token, "User-Agent": "agent_2"},
    )

    assert response.status == HTTPStatus.FORBIDDEN
