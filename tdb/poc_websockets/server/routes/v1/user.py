import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from tdb.poc_websockets.server import database
from tdb.poc_websockets.server.models import DeleteResponse
from tdb.poc_websockets.server.models.user import UserCreate, UserRead, UserRepository, UserUpdate

router = APIRouter(
    prefix='/v1/users',
    tags=['users'],
)


@router.post(
    '/',
    summary='Create a new User',
    status_code=status.HTTP_201_CREATED,
)
async def post(data: UserCreate, db: Annotated[AsyncSession, Depends(database.get_session)]) -> UserRead:
    model = await UserRepository(session=db).create(data)
    logging.debug(model)
    return UserRead.model_validate(model)


@router.get(
    '/{ident}',
    summary='Get a User',
    status_code=status.HTTP_200_OK,
)
async def get(ident: UUID, db: Annotated[AsyncSession, Depends(database.get_session)]) -> UserRead:
    model = await UserRepository(session=db).read(ident)
    return UserRead.model_validate(model)


@router.patch(
    '/{ident}',
    summary='Update a User',
    status_code=status.HTTP_200_OK,
)
async def patch(ident: UUID, data: UserUpdate, db: Annotated[AsyncSession, Depends(database.get_session)]) -> UserRead:
    model = await UserRepository(session=db).update(ident, data)
    return UserRead.model_validate(model)


@router.delete(
    '/{ident}',
    summary='Delete a User',
    status_code=status.HTTP_200_OK,
)
async def delete(ident: UUID, db: Annotated[AsyncSession, Depends(database.get_session)]) -> DeleteResponse:
    await UserRepository(session=db).delete(ident)
    return DeleteResponse(deleted=1)
