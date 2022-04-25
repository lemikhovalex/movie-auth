from http import HTTPStatus

import pytest

# All test coroutines will be treated as marked with this decorator.
pytestmark = pytest.mark.asyncio

USER_ID = "14"
USER = {
    "credentials": {"login": "test1", "password": "test1"},
    "user_data": {"first_name": "13", "second_name": "Est"},
}
NEW_USER_DATA = {"first_name": "14", "second_name": "TEst"}


async def test_user_create(make_request):
    global USER_ID
    global USER

    response = await make_request("post")(
        "users",
        json=USER,
    )

    USER_ID = response.body["user_id"]

    assert response.status == HTTPStatus.CREATED


async def test_user_data(make_request, access_token):

    global USER_ID
    global USER

    response = await make_request("get")(
        f"users/{USER_ID}",
        headers={"Authorization": access_token},
    )

    assert response.body == USER["user_data"]
    assert response.status == HTTPStatus.OK


async def test_update_user_data(make_request, access_token):

    global USER_ID
    global NEW_USER_DATA

    response = await make_request("put")(
        f"users/{USER_ID}",
        json=NEW_USER_DATA,
        headers={"Authorization": access_token},
    )

    assert response.status == HTTPStatus.OK


async def test_user_data_after_upd(make_request):

    global USER_ID
    global NEW_USER_DATA

    response = await make_request("get")(
        f"users/{USER_ID}",
    )

    assert response.body == NEW_USER_DATA
    assert response.status == HTTPStatus.OK


async def test_user_delete(make_request, access_token):

    global USER_ID

    response = await make_request("delete")(
        f"users/{USER_ID}",
        headers={"Authorization": access_token},
    )

    assert response.status == HTTPStatus.OK


async def test_user_data_after_del(make_request):

    global USER_ID

    response = await make_request("get")(
        f"users/{USER_ID}",
    )

    assert response.status == HTTPStatus.NOT_FOUND


async def test_login_after_del(make_request):
    response = await make_request("post")("auth/login", json=USER["credentials"])

    assert response.status == HTTPStatus.NOT_FOUND
