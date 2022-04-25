import json

from services.blacklist import (
    ACCESS_REVOKED,
    LOG_OUT_ALL,
    UPD_PAYLOAD,
    AccessForBlackList,
)
from utils.tokens import check_validity_and_payload, get_access_and_refresh_jwt


def check(request, roles_getter) -> (str, list, int):
    access_token = request.headers.get("Authorization") or ""
    agent = request.headers.get("User-Agent")
    new_token = None

    is_valid, payload = check_validity_and_payload(access_token)
    black_list_info = AccessForBlackList.from_dict(**payload)
    if not is_valid:
        return "go log in", 403
    user_id = payload["user_id"]
    if not ACCESS_REVOKED.is_ok(access_token):
        print("revoked")
        return ("revoked", 403)

    if not LOG_OUT_ALL.is_ok(payload=black_list_info):
        ACCESS_REVOKED.add(token=access_token)
        return ("requested logout", 403)

    if not UPD_PAYLOAD.is_ok(payload=black_list_info):
        ACCESS_REVOKED.add(access_token)
        new_token, _ = get_access_and_refresh_jwt(user_id, roles_getter)
        UPD_PAYLOAD.process_update(user_id=user_id, agent=agent)
    return json.dumps({"new_access_token": new_token, "payload": payload}), 200
