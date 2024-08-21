import jwt
from datetime import datetime, timedelta
import uuid

from config import settings


def generate_cookie_session_id():
    return uuid.uuid4().hex


# ключ сразу читается и передается благодаря pathlib
def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
    expire_minutes: int = settings.auth_jwt.access_token_expire_min,
):
    to_encode = payload.copy()
    iat = datetime.utcnow()  # время создания токена
    expire = iat + timedelta(minutes=expire_minutes)  # время истечения токена
    to_encode.update(iat=iat, exp=expire)
    encoded_jwt = jwt.encode(payload=to_encode, key=private_key, algorithm=algorithm)
    return encoded_jwt


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
):
    decoded_jwt = jwt.decode(token, key=public_key, algorithms=[algorithm])
    return decoded_jwt
