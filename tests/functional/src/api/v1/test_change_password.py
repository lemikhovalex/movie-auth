from http import HTTPStatus

import pytest

# All test coroutines will be treated as marked with this decorator.
pytestmark = pytest.mark.asyncio

old_password = "test1"
new_password = "test2"

FIRST_TOKEN = None
SECOND_TOKEN = None


async def test_user_create(make_request):
    response = await make_request("post")(
        "users",
        json={
            "credentials": {"login": "test1", "password": old_password},
            "user_data": {"first_name": "13", "second_name": "Est"},
        },
    )

    assert response.status == HTTPStatus.CREATED


async def test_login(make_request):
    global FIRST_TOKEN
    response = await make_request("post")(
        "auth/login",
        json={"login": "test1", "password": old_password},
    )
    FIRST_TOKEN = response.body["access_token"]

    assert response.status == HTTPStatus.OK


async def test_one_more_login(make_request):
    global SECOND_TOKEN
    response = await make_request("post")(
        "auth/login",
        json={"login": "test1", "password": old_password},
    )
    SECOND_TOKEN = response.body["access_token"]

    assert response.status == HTTPStatus.OK


async def test_change_password(make_request):
    response = await make_request("post")(
        "auth/change-password",
        headers={"Authorization": FIRST_TOKEN},
        json={"password": new_password},
    )
    assert response.status == HTTPStatus.OK


async def test_change_password_again(make_request):
    response = await make_request("post")(
        "auth/change-password",
        headers={"Authorization": SECOND_TOKEN},
        json={"password": new_password},
    )
    assert response.status == HTTPStatus.FORBIDDEN


async def test_login_again(make_request):
    global FIRST_TOKEN
    response = await make_request("post")(
        "auth/login",
        json={"login": "test1", "password": old_password},
    )

    assert response.status == HTTPStatus.FORBIDDEN
