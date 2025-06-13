from pydantic import BaseModel
class GoalHistoryRecord(BaseModel):
    period: str  # 'YYYY-MM'
    real: float
    goal: float