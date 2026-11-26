from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

    model_config = ConfigDict(extra='forbid')

class UserUpdate(BaseModel):
    email: EmailStr | None = None

    model_config = ConfigDict(extra='forbid')


class UserRead(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=128)

    model_config = ConfigDict(extra='forbid')


class AdminCreate(UserCreate):
    is_admin: bool = True

    model_config = ConfigDict(extra='forbid')
