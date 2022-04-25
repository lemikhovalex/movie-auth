from http import HTTPStatus

import pytest

# All test coroutines will be treated as marked with this decorator.
pytestmark = pytest.mark.asyncio

old_login = "test1"
new_login = "test2"

FIRST_TOKEN = None
SECOND_TOKEN = None


async def test_user_create(make_request):
    response = await make_request("post")(
        "users",
        json={
            "credentials": {"login": old_login, "password": "test1"},
            "user_data": {"first_name": "13", "second_name": "Est"},
        },
    )

    assert response.status == HTTPStatus.CREATED


async def test_login(make_request):
    global FIRST_TOKEN
    response = await make_request("post")(
        "auth/login",
        json={"login": old_login, "password": "test1"},
    )
    FIRST_TOKEN = response.body["access_token"]

    assert response.status == HTTPStatus.OK


async def test_one_more_login(make_request):
    global SECOND_TOKEN
    response = await make_request("post")(
        "auth/login",
        json={"login": old_login, "password": "test1"},
    )
    SECOND_TOKEN = response.body["access_token"]

    assert response.status == HTTPStatus.OK


async def test_change_login(make_request):
    response = await make_request("post")(
        "auth/change-login",
        headers={"Authorization": FIRST_TOKEN},
        json={"login": new_login},
    )
    assert response.status == HTTPStatus.OK


async def test_change_login_again(make_request):
    response = await make_request("post")(
        "auth/change-login",
        headers={"Authorization": SECOND_TOKEN},
        json={"login": new_login},
    )
    assert response.status == HTTPStatus.OK


async def test_login_again(make_request):
    global FIRST_TOKEN
    response = await make_request("post")(
        "auth/login",
        json={"login": "test1", "password": "test1"},
    )

    assert response.status == HTTPStatus.NOT_FOUND
