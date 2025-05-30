from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr
class ExpenseBase(BaseModel):
    date: date
    amount: float
    category: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    user_id: int

class ExpenseRead(ExpenseBase):
    user_id: int

    class Config:
        orm_mode = True