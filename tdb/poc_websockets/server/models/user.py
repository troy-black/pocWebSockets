from pydantic import EmailStr, field_serializer
from sqlalchemy import VARCHAR, Column
from sqlmodel import Field, SQLModel, select

from tdb.poc_websockets.server.models import BaseIdModel, BaseRepository, TimestampMixin


class UserBase(SQLModel):
    email: EmailStr = Field(sa_column=Column(VARCHAR, unique=True))
    name: str = Field(sa_column=Column(VARCHAR, index=True, nullable=False))


class UserDefault(UserBase):
    disabled: bool = False


class UserCreate(UserBase):
    password: str


class UserRead(BaseIdModel, UserDefault, TimestampMixin):
    pass


class UserUpdate(BaseIdModel, UserCreate, TimestampMixin):
    pass


class User(BaseIdModel, UserCreate, TimestampMixin, table=True):
    disabled: bool = False

    @field_serializer('password', when_used='always')
    def serialize_password(self, _password: str) -> str:
        return '*****'


class UserRepository(BaseRepository[UserCreate, UserUpdate, User]):
    table_model = User

    async def create(self, model: UserCreate) -> User:
        from tdb.poc_websockets.server.auth import get_password_hash

        model.password = get_password_hash(model.password)
        return await super().create(model)

    async def get_by_email(self, email: str) -> User:
        statement = select(self.table_model).where(self.table_model.email == email)
        result = await self.session.execute(statement)
        return result.scalars().one()
