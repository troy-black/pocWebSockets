from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from tdb.poc_websockets.server import auth, database
from tdb.poc_websockets.server.config import settings
from tdb.poc_websockets.server.models.auth_token import Logout, Token
from tdb.poc_websockets.server.models.user import User, UserRead, UserRepository

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)


@router.post('/login')
async def login_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(database.get_session)],
) -> Token:
    user = await UserRepository(session=db).get_by_email(form_data.username)

    if not auth.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid Credentials')

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(data={'sub': user.email}, expires_delta=access_token_expires)

    # set HttpOnly cookie in response
    response.set_cookie(
        key='access_token',
        value=f'Bearer {access_token}',
        httponly=True,
    )
    return Token(access_token=access_token, token_type='bearer')


@router.delete('/logout')
async def logout(response: Response) -> Logout:
    response.delete_cookie('access_token')
    return Logout()


@router.get('/me/')
async def current_user(user: Annotated[User, Depends(auth.get_current_active_user)]) -> UserRead:
    return UserRead.model_validate(user)


@router.get('/users/me/items/')
async def read_own_items(user: Annotated[User, Depends(auth.get_current_active_user)]) -> list[dict[str, str]]:
    return [{'item_id': 'Foo', 'owner': user.email}]
