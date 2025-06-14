from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, date
from typing import List
from db.db import get_db
from models.income import Income
from schemas.income import IncomeRead
from fastapi.security import HTTPAuthorizationCredentials
from .auth import security

router = APIRouter()

@router.get("/{user_id}/current-month", response_model=float)
async def get_current_month_income(
    user_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Obtiene el total de ingresos del mes actual para un usuario"""
    today = date.today()
    first_day = today.replace(day=1)
    last_day = today.replace(day=28)  # Empezamos con el día 28
    
    # Ajustamos para el último día del mes
    while True:
        try:
            last_day = last_day.replace(day=last_day.day + 1)
        except ValueError:
            break
    last_day = last_day.replace(day=last_day.day - 1)
    
    total = db.query(func.coalesce(func.sum(Income.amount), 0)).filter(
        Income.user_id == user_id,
        Income.date >= first_day,
        Income.date <= last_day
    ).scalar()
    
    return total if total is not None else 0.0
