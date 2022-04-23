from typing import Any


def get_access_jwt(payload):
    return payload  # TODO implement


def get_refresh_jwt(payload):
    return payload  # TODO implement


def check_validity_and_payload(token) -> (bool, Any):
    return (True, {"user_id": token})
