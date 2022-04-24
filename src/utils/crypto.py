import hashlib
import os
from typing import Optional


def cypher_password(password: str, salt: Optional[str] = None) -> str:
    if salt is None:
        salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return salt + key


def check_password(password: str, password_encoded: str) -> bool:
    salt_from_storage = password_encoded[:32]
    new_key = cypher_password(password=password, salt=salt_from_storage)
    return password_encoded == new_key
