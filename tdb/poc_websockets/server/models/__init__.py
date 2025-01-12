from datetime import UTC, datetime
from typing import Generic, Self, TypeVar
from uuid import UUID

import uuid_utils
from pydantic import BaseModel
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Field, SQLModel, select


class IdMixin(SQLModel):
    id: UUID = Field(
        default_factory=uuid_utils.uuid7,
        primary_key=True,
        index=True,
        nullable=False,
    )


class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.now(UTC),
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), onupdate=lambda: datetime.now(UTC)),
        default_factory=lambda: datetime.now(UTC),
    )


class DeleteResponse(BaseModel):
    deleted: int


class BaseIdModel(IdMixin, BaseModel):
    def update(self, model: BaseModel) -> Self:
        for name, value in model.model_dump(exclude_unset=True).items():
            existing_val = getattr(self, name)
            if existing_val != value:
                setattr(self, name, value)

        return self


CreateModel = TypeVar('CreateModel', bound=SQLModel)
ReadModel = TypeVar('ReadModel', bound=BaseIdModel)
UpdateModel = TypeVar('UpdateModel', bound=BaseModel)
TableModel = TypeVar('TableModel', bound=BaseIdModel)


class BaseRepository(Generic[CreateModel, UpdateModel, TableModel]):
    table_model: type[TableModel]

    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session

    async def create(self, model: CreateModel) -> TableModel:
        table_model: TableModel = self.table_model.model_validate(model)
        self.session.add(table_model)
        await self.session.commit()
        await self.session.refresh(table_model)
        return table_model

    async def read(self, ident: UUID) -> TableModel:
        statement = select(self.table_model).where(self.table_model.id == ident)
        result = await self.session.execute(statement)
        return result.scalars().one()

    async def update(self, ident: UUID, model: UpdateModel) -> TableModel:
        table_model = await self.read(ident)
        table_model.update(model)
        self.session.add(table_model)
        await self.session.commit()
        await self.session.refresh(table_model)

        return table_model

    async def delete(self, ident: UUID) -> None:
        table_model = await self.read(ident)
        await self.session.delete(table_model)
        await self.session.commit()
