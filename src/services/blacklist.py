import inspect
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import redis

from config.db import ACCESS_TOKEN_EXP, REFRESH_TOKEN_EXP
from config.formatting import DATE_TIME_FORMAT
from db.redis import log_out, revoked_access, upd_payload


@dataclass
class AccessForBlackList:
    user_id: str
    iat: int
    exp: int

    @classmethod
    def from_dict(cls, **kwargs):
        return cls(
            **{
                k: v
                for k, v in kwargs.items()
                if k in inspect.signature(cls).parameters
            }
        )


class BaseDeviceBlackList(ABC):
    @abstractmethod
    def add(self, **kwargs) -> None:
        pass

    @abstractmethod
    def process_update(self, **kwargs):
        pass

    @abstractmethod
    def is_ok(self, **kwargs) -> bool:
        pass


class UserBlackList(BaseDeviceBlackList):
    def __init__(
        self, id_storage: redis.Redis, device_storage: Optional[redis.Redis] = None
    ):

        self.id_storage = id_storage
        self.device_storage = device_storage

    def add(self, payload: AccessForBlackList) -> None:
        self.id_storage.setex(
            payload.user_id,
            REFRESH_TOKEN_EXP,
            datetime.strftime(datetime.now(), DATE_TIME_FORMAT),
        )

    def process_update(self, user_id: uuid.UUID, **kwargs):
        pass

    def is_ok(self, payload: AccessForBlackList, **kwargs) -> bool:
        str_time = self.id_storage.get(payload.user_id)
        iat = datetime.fromtimestamp(payload.iat)

        if str_time is None:
            return True  # no request to logout for this user
        set_time = datetime.strptime(str_time, DATE_TIME_FORMAT)
        print("iat: {i}\nset: {s}".format(i=iat, s=set_time))
        if iat < set_time:
            print("iat > set")
            return False  # logged in after request on logout
        return True


class RevokedAccessBlackList(BaseDeviceBlackList):
    def __init__(self, token_storage: redis.Redis):

        self.token_storage = token_storage

    def add(self, token: str) -> None:
        if token != "":
            self.token_storage.setex(
                token,
                ACCESS_TOKEN_EXP,
                "revoked",
            )

    def process_update(self, user_id: uuid.UUID, agent: str):
        pass

    def is_ok(self, token: str) -> bool:
        return not bool(self.token_storage.exists(token))


LOG_OUT_ALL = UserBlackList(
    id_storage=log_out.user_ids, device_storage=log_out.user_agents
)

UPD_PAYLOAD = UserBlackList(
    id_storage=upd_payload.user_ids, device_storage=upd_payload.user_agents
)

ACCESS_REVOKED = RevokedAccessBlackList(token_storage=revoked_access)
