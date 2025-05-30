from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr
class InvestmentBase(BaseModel):
    date: date
    amount: float
    category: Optional[str] = None

class InvestmentCreate(InvestmentBase):
    user_id: int

class InvestmentRead(InvestmentBase):
    user_id: int

    class Config:
        orm_mode = True
