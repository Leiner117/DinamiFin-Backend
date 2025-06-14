from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True

class PerfilUpdate(BaseModel):
    email: str | None = None
    username: str | None = None
    password: str | None = None
    meta_gasto: float | None = None
    meta_ahorro: float | None = None
    meta_inversion: float | None = None
