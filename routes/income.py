from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, date
from typing import List
from db.db import get_db
from models.income import Income
from schemas.income import IncomeCreate, IncomeRead
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
    last_day = today.replace(day=28)
    
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

@router.post("/{user_id}", response_model=IncomeRead)
async def create_income(
    user_id: int,
    income: IncomeCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Crea un nuevo registro de ingreso para un usuario"""
    if income.amount < 0:
        raise HTTPException(status_code=400, detail="El monto no puede ser negativo")
    
    db_income = Income(
        user_id=user_id,
        date=income.date,
        amount=income.amount
    )
    
    try:
        db.add(db_income)
        db.commit()
        db.refresh(db_income)
        return db_income
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{user_id}/{date}", response_model=IncomeRead)
async def update_income(
    user_id: int,
    date: date,
    income: IncomeCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Actualiza un registro de ingreso existente"""
    if income.amount < 0:
        raise HTTPException(status_code=400, detail="El monto no puede ser negativo")
    
    db_income = db.query(Income).filter(
        Income.user_id == user_id,
        Income.date == date
    ).first()
    
    if not db_income:
        raise HTTPException(status_code=404, detail="Registro de ingreso no encontrado")
    
    db_income.amount = income.amount
    db_income.date = income.date
    
    try:
        db.commit()
        db.refresh(db_income)
        return db_income
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
