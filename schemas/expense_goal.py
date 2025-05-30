from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr

class ExpenseGoalBase(BaseModel):
    date: date
    value: float

class ExpenseGoalCreate(ExpenseGoalBase):
    user_id: int

class ExpenseGoalRead(ExpenseGoalBase):
    user_id: int

    class Config:
        orm_mode = True