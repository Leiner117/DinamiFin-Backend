from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr

class IncomeBase(BaseModel):
    date: date
    amount: float

class IncomeCreate(IncomeBase):
    pass

class IncomeRead(IncomeBase):
    user_id: int

    class Config:
        orm_mode = True