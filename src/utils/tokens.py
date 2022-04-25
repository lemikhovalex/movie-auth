import uuid
from datetime import datetime, timedelta
from typing import Callable, Optional, Tuple

import jwt
from jwt.exceptions import DecodeError, InvalidSignatureError

from config.db import ACCESS_TOKEN_EXP, REFRESH_TOKEN_EXP
from config.secrets import SECRET_SIGNATURE


def _get_access_jwt(
    user_id: uuid.UUID,
    roles_getter: Callable[[str], Tuple[dict, int]],
    roles: Optional[list[int]] = None,
    time_out: int = ACCESS_TOKEN_EXP,
) -> (str, int):
    if roles is None:
        resp, code = roles_getter(str(user_id))
        if code != 200:
            return resp, code

    roles = resp.json
    payload = {
        "exp": datetime.now() + timedelta(seconds=time_out),
        "iat": datetime.now(),
        "user_id": str(user_id),
        "roles": roles,
    }
    return jwt.encode(
        payload,
        SECRET_SIGNATURE,
        algorithm="HS256",
    )


def _get_refresh_jwt(user_id, roles_getter: Callable[[str], Tuple[dict, int]]):
    return _get_access_jwt(
        user_id=user_id, time_out=REFRESH_TOKEN_EXP, roles_getter=roles_getter
    )


def get_access_and_refresh_jwt(
    user_id: uuid.UUID,
    roles_getter: Callable[[str], Tuple[dict, int]],
):
    return _get_refresh_jwt(user_id, roles_getter=roles_getter), _get_refresh_jwt(
        user_id, roles_getter=roles_getter
    )


def check_validity_and_payload(token) -> (bool, dict):
    is_ok = True
    payload = {}
    try:
        payload = jwt.decode(token, SECRET_SIGNATURE, algorithms=["HS256"])
    except (
        DecodeError,
        InvalidSignatureError,
    ):
        is_ok = False
    return (is_ok, payload)
