from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr
class SavingGoalBase(BaseModel):
    date: date
    value: float

class SavingGoalCreate(SavingGoalBase):
    user_id: int

class SavingGoalRead(SavingGoalBase):
    user_id: int

    class Config:
        orm_mode = True