from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List, Optional, Dict
from db import get_db 
from models import Income, Expense, Saving, Investment, ExpenseGoal, SavingGoal, InvestmentGoal
from schemas import FinanceHistoryRecord, GoalHistoryRecord 

router = APIRouter(
    prefix="/history",
    tags=["Finance History"]
)

# Helper para calcular fecha de inicio según periodo (en meses)
def periodo_to_start_date(periodo: str):
    hoy = date.today()
    if periodo == "1m":
        return hoy - timedelta(days=30)
    elif periodo == "6m":
        return hoy - timedelta(days=180)
    elif periodo == "1y":
        return hoy - timedelta(days=365)
    elif periodo == "3y":
        return hoy - timedelta(days=1095)
    elif periodo == "5y":
        return hoy - timedelta(days=1825)
    return hoy.replace(day=1)

def group_by_month(records, field="amount", start_date=None, end_date=None):
    res = {}
    current = start_date.replace(day=1)
    while current <= end_date:
        key = f"{current.year}-{current.month:02d}"
        res[key] = 0
        current += timedelta(days=32)
        current = current.replace(day=1)
    for r in records:
        key = f"{r.date.year}-{r.date.month:02d}"
        if key in res:
            res[key] += getattr(r, field)
    return [{"period": k, "total": v} for k, v in sorted(res.items())]

# HISTÓRICO GENERAL
@router.get("/income/{user_id}", response_model=List[FinanceHistoryRecord])
def get_income_history(
    user_id: int,
    periodo: str = Query("1y", regex="^(1m|6m|1y|3y|5y)$"),
    db: Session = Depends(get_db),
):
    start = periodo_to_start_date(periodo)
    end = date.today()  # Fecha final es hoy
    res = db.query(Income).filter(
        Income.user_id == user_id, 
        Income.date >= start,
        Income.date <= end  # Filtra hasta hoy
    ).all()
    return group_by_month(res, "amount", start, end)  # Pasa fechas

@router.get("/expense/{user_id}", response_model=List[FinanceHistoryRecord])
def get_expense_history(
    user_id: int,
    periodo: str = Query("1y", regex="^(1m|6m|1y|3y|5y)$"),
    db: Session = Depends(get_db),
):
    start = periodo_to_start_date(periodo)
    end = date.today()
    res = db.query(Expense).filter(Expense.user_id == user_id, Expense.date >= start, Expense.date <= end).all()
    return group_by_month(res, "amount", start, end)

@router.get("/saving/{user_id}", response_model=List[FinanceHistoryRecord])
def get_saving_history(
    user_id: int,
    periodo: str = Query("1y", regex="^(1m|6m|1y|3y|5y)$"),
    db: Session = Depends(get_db),
):
    start = periodo_to_start_date(periodo)
    end = date.today() 
    res = db.query(Saving).filter(Saving.user_id == user_id, Saving.date >= start).all()
    return group_by_month(res, "amount", start, end)

@router.get("/investment/{user_id}", response_model=List[FinanceHistoryRecord])
def get_investment_history(
    user_id: int,
    periodo: str = Query("1y", regex="^(1m|6m|1y|3y|5y)$"),
    db: Session = Depends(get_db),
):
    start = periodo_to_start_date(periodo)
    end = date.today() 
    res = db.query(Investment).filter(Investment.user_id == user_id, Investment.date >= start).all()
    return group_by_month(res, "amount", start, end)

# GOALS

def group_goal_by_month(real, goal):
    out = {}
    # Agrupa ambos por mes
    for r in real:
        key = f"{r.date.year}-{r.date.month:02d}"
        out.setdefault(key, {"real": 0, "goal": 0})
        out[key]["real"] += getattr(r, "amount", getattr(r, "value", 0))
    for g in goal:
        key = f"{g.date.year}-{g.date.month:02d}"
        out.setdefault(key, {"real": 0, "goal": 0})
        out[key]["goal"] += getattr(g, "value", getattr(g, "amount", 0))
    # Ordena y devuelve lista
    return [
        {"period": k, "real": v["real"], "goal": v["goal"]}
        for k, v in sorted(out.items())
    ]

@router.get("/expense_goal/{user_id}", response_model=List[GoalHistoryRecord])
def get_expense_goal_history(
    user_id: int,
    periodo: str = Query("1y", regex="^(1m|6m|1y|3y|5y)$"),
    db: Session = Depends(get_db),
):
    start = periodo_to_start_date(periodo)
    real = db.query(Expense).filter(Expense.user_id == user_id, Expense.date >= start).all()
    goals = db.query(ExpenseGoal).filter(ExpenseGoal.user_id == user_id, ExpenseGoal.date >= start).all()
    return group_goal_by_month(real, goals)

@router.get("/saving_goal/{user_id}", response_model=List[GoalHistoryRecord])
def get_saving_goal_history(
    user_id: int,
    periodo: str = Query("1y", regex="^(1m|6m|1y|3y|5y)$"),
    db: Session = Depends(get_db),
):
    start = periodo_to_start_date(periodo)
    real = db.query(Saving).filter(Saving.user_id == user_id, Saving.date >= start).all()
    goals = db.query(SavingGoal).filter(SavingGoal.user_id == user_id, SavingGoal.date >= start).all()
    return group_goal_by_month(real, goals)

@router.get("/investment_goal/{user_id}", response_model=List[GoalHistoryRecord])
def get_investment_goal_history(
    user_id: int,
    periodo: str = Query("1y", regex="^(1m|6m|1y|3y|5y)$"),
    db: Session = Depends(get_db),
):
    start = periodo_to_start_date(periodo)
    real = db.query(Investment).filter(Investment.user_id == user_id, Investment.date >= start).all()
    goals = db.query(InvestmentGoal).filter(InvestmentGoal.user_id == user_id, InvestmentGoal.date >= start).all()
    return group_goal_by_month(real, goals)