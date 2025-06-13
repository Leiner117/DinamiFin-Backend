from datetime import date
from pydantic import BaseModel

class InvestmentGoalBase(BaseModel):
    date: date
    value: float

class InvestmentGoalCreate(InvestmentGoalBase):
    user_id: int

class InvestmentGoalRead(InvestmentGoalBase):
    user_id: int

    class Config:
        from_attributes = True  # Pydantic v2
