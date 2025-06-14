from pydantic import BaseModel
class GoalHistoryRecord(BaseModel):
    period: str          
    real: float           
    goal: float           
    income: float