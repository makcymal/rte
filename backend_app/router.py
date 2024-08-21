import datetime
import logging

from fastapi import APIRouter, HTTPException, Depends
from jwt import InvalidTokenError
from python_freeipa import ClientMeta
from python_freeipa.exceptions import InvalidSessionPassword
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from models import User
from config import settings
from auth import encode_jwt, decode_jwt
from streaming.clients import ws_router


logger = logging.getLogger(__name__)

router = APIRouter()
router.include_router(ws_router)


@router.get("/")
async def get():
    logger.info("GET: /")
    return {"hello": "hello"}


ipa_client = ClientMeta("ipa1-hlit.jinr.ru")


@router.post("/api/token/login")
async def login(user: User):
    logger.info("POST: /api/token/login")
    try:
        ipa_client.login(user.login, user.password)
    except InvalidSessionPassword:
        return {"status": "ERROR", "data": None, "details": "Invalid login or password"}
    user_data = ipa_client.user_show(user.login)["result"]
    user_public_data = {
        "sub": user_data["uid"][0],
        "id": user_data["uid"][0],
        "name": user_data["displayname"][0],
        "mail": user_data["mail"][0],
        "homedirectory": user_data["homedirectory"][0],
    }
    logger.info(f"Client {user_public_data['name']} logged in")

    access_token = encode_jwt(user_public_data)

    expires = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=settings.auth_jwt.access_token_expire_min
    )

    content = {"status": "OK", "data": None, "details": "user authorized"}

    response = JSONResponse(content=content)
    response.set_cookie(
        key="access_token",
        value=f"{access_token}",
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
    )
    return response


@router.post("/api/token/logout")
async def logout():
    logger.info("POST: /api/token/logout")
    content = {"status": "OK", "data": None, "details": "user logged out"}

    response = JSONResponse(content=content)

    # expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=5)

    response.delete_cookie(
        key="access_token", secure=True, httponly=True, samesite="none", path="/"
    )
    return response


def get_data_from_jwt_cookie(request: Request):
    token = request.cookies.get("access_token")
    try:
        public_user_data = decode_jwt(token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized or invalid token",
        )
    del public_user_data["sub"]
    return public_user_data


@router.get("/check-cookie-login")
async def check_cookie_login(user_data: dict = Depends(get_data_from_jwt_cookie)):
    logger.info("GET: /check-cookie-login")
    logger.info(f"Client {user_data['name']} checked cookie login")
    return {"status": "OK", "data": user_data, "details": "user authorized"}
