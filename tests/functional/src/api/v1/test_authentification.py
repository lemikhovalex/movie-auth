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


async def test_logout(make_request, access_token):
    response = await make_request("post")(
        "auth/logout",
        headers={"Authorization": access_token},
    )

    assert response.status == HTTPStatus.OK


async def test_check_notauthorized(make_request, access_token):
    response = await make_request("post")(
        "auth/check",
        headers={"Authorization": access_token},
    )

    assert response.status == HTTPStatus.FORBIDDEN
