import json
import uuid
from abc import ABC, abstractmethod
from datetime import datetime

import redis

from config.db import ACCESS_TOKEN_EXP, REFRESH_TOKEN_EXP
from config.formatting import DATE_TIME_FROMAT
from db.redis import log_out, revoked_access, upd_payload


class BaseDeviceBlackList(ABC):
    @abstractmethod
    def add(self, **kwargs) -> None:
        pass

    @abstractmethod
    def process_update(self, **kwargs):
        pass

    @abstractmethod
    def check(self, **kwargs) -> bool:
        pass


class UserDeviceBlackList(BaseDeviceBlackList):
    def __init__(self, id_storage: redis.Redis, device_storage: redis.Redis):

        self.id_storage = id_storage
        self.device_storage = device_storage

    def add(self, user_id: uuid.UUID) -> None:
        self.id_storage.setex(
            str(user_id),
            REFRESH_TOKEN_EXP,
            datetime.strftime(datetime.now(), DATE_TIME_FROMAT),
        )

    def process_update(self, user_id: uuid.UUID, agent: str):
        if self.check(user_id, agent):
            self.device_storage.setex(
                self._get_uid_agent_str(user_id, agent),
                REFRESH_TOKEN_EXP,
                datetime.strftime(datetime.now(), DATE_TIME_FROMAT),
            )

    def check(self, user_id: uuid.UUID, agent: str) -> bool:
        str_time = self.id_storage.get(str(user_id))
        if str_time is None:
            return False
        set_time = datetime.strptime(str_time, DATE_TIME_FROMAT)

        last_action = self.device_storage.get(
            self._get_uid_agent_str(user_id, agent),
        )
        if last_action is None:
            return False
        last_action = datetime.strptime(last_action, DATE_TIME_FROMAT)

        if last_action > set_time:
            return True
        return True

    def _get_uid_agent_str(self, user_id: uuid.UUID, agent: str):
        return json.dumps({"user_id": user_id, agent: "agent"})


class RevokedAccessBlackList(BaseDeviceBlackList):
    def __init__(self, token_storage: redis.Redis):

        self.token_storage = token_storage

    def add(self, token: str) -> None:
        if token != "":
            self.token_storage.setex(
                token,
                ACCESS_TOKEN_EXP,
                "",
            )

    def process_update(self, user_id: uuid.UUID, agent: str):
        pass

    def check(self, token: str) -> bool:
        return bool(self.token_storage.exists(token))


LOG_OUT_ALL = UserDeviceBlackList(
    id_storage=log_out.user_ids, device_storage=log_out.user_agents
)

UPD_PAYLOAD = UserDeviceBlackList(
    id_storage=upd_payload.user_ids, device_storage=upd_payload.user_agents
)

ACCESS_ROVEKED = RevokedAccessBlackList(token_storage=revoked_access)
