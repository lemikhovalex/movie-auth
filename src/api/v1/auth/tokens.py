import uuid
from datetime import datetime, timedelta
from typing import Optional

import jwt

from api.v1.users.roles import get_roles
from config.db import ACCESS_TOKEN_EXP, REFRESH_TOKEN_EXP
from config.formatting import DATE_TIME_FROMAT
from config.secrets import SECRET_SIGNATURE


def _get_access_jwt(
    user_id: uuid.UUID,
    roles: Optional[list[int]] = None,
    time_out: int = ACCESS_TOKEN_EXP,
) -> (str, int):
    if roles is None:
        resp, code = get_roles(str(user_id))
        if code != 200:
            return resp, code

    roles = resp.json
    exp = datetime.strftime(
        datetime.now() + timedelta(seconds=time_out),
        DATE_TIME_FROMAT,
    )
    i_at = datetime.strftime(
        datetime.now(),
        DATE_TIME_FROMAT,
    )
    payload = {
        "exp": exp,
        "iat": i_at,
        "usr_id": str(user_id),
        "roles": roles,
    }
    return jwt.encode(payload, SECRET_SIGNATURE, algorithm="HS256")


def _get_refresh_jwt(user_id):
    return _get_access_jwt(user_id=user_id, time_out=REFRESH_TOKEN_EXP)


def get_access_and_refresh_jwt(user_id: uuid.UUID):
    return _get_refresh_jwt(user_id), _get_refresh_jwt(user_id)


def check_validity_and_payload(token) -> (bool, dict):
    return (True, {"user_id": token})
