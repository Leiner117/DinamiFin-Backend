from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr

class SavingBase(BaseModel):
    date: date
    amount: float
    category: Optional[str] = None

class SavingCreate(SavingBase):
    user_id: int

class SavingRead(SavingBase):
    user_id: int

    class Config:
        orm_mode = True
