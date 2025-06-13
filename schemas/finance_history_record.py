from pydantic import BaseModel

class FinanceHistoryRecord(BaseModel):
    period: str  # 'YYYY-MM'
    total: float