import logging
from datetime import UTC, datetime, timedelta
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.openapi.models import OAuthFlowPassword
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from jwt.exceptions import InvalidTokenError
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from tdb.poc_websockets.server import database
from tdb.poc_websockets.server.config import settings
from tdb.poc_websockets.server.models.user import User, UserRepository

logger = logging.getLogger(__name__)


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        token_url: str,
        scheme_name: str | None = None,
        scopes: dict[str, str] | None = None,
        *,
        auto_error: bool = True,
    ) -> None:
        if not scopes:
            scopes = {}

        flow_password = OAuthFlowPassword(tokenUrl=token_url, scopes=scopes)
        flows = OAuthFlowsModel(password=flow_password)
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> str | None:
        # changed to accept access token from httpOnly Cookie
        authorization = request.cookies.get('access_token')
        logger.debug('access_token is %s', authorization)

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != 'bearer':
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail='Not authenticated',
                    headers={'WWW-Authenticate': 'Bearer'},
                )
            return None

        return param


oauth2_bearer = OAuth2PasswordBearerWithCookie(token_url='/auth/login')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        bytes(plain_password, encoding='utf-8'),
        bytes(hashed_password, encoding='utf-8'),
    )


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(
        bytes(password, encoding='utf-8'),
        bcrypt.gensalt(),
    ).decode('utf-8')


def create_access_token(data: dict[str, EmailStr], expires_delta: timedelta | None = None) -> str:
    to_encode: dict[str, EmailStr | datetime] = dict(data)
    now = datetime.now(UTC)
    expire = now + expires_delta if expires_delta else now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)],
    db: Annotated[AsyncSession, Depends(database.get_session)],
) -> User:
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get('sub')
        if email is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception from None

    return await UserRepository(session=db).get_by_email(email)


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail='Inactive user')

    return current_user
