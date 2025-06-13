from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List, Optional, Dict
from db import get_db 
from ..models import Income, Expense, Saving, Investment, ExpenseGoal, SavingGoal, InvestmentGoal
from ..schemas import FinanceHistoryRecord, GoalHistoryRecord 

router = APIRouter(
    prefix="/history",
    tags=["Finance History"]
)

# Helper para calcular fecha de inicio según periodo (en meses)
def periodo_to_start_date(periodo: str):
    hoy = date.today()
    if periodo == "1m":
        return hoy.replace(day=1)
    elif periodo == "6m":
        month = hoy.month - 5 if hoy.month > 5 else hoy.month + 7
        year = hoy.year if hoy.month > 5 else hoy.year - 1
        return date(year, month, 1)
    elif periodo == "1y":
        return date(hoy.year - 1, hoy.month, 1)
    elif periodo == "3y":
        return date(hoy.year - 3, hoy.month, 1)
    elif periodo == "5y":
        return date(hoy.year - 5, hoy.month, 1)
    return hoy.replace(day=1)

# Generic group by year-month
def group_by_month(records, field="amount"):
    res = {}
    for r in records:
        key = f"{r.date.year}-{r.date.month:02d}"
        res.setdefault(key, 0)
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
    res = db.query(Income).filter(Income.user_id == user_id, Income.date >= start).all()
    return group_by_month(res)

@router.get("/expense/{user_id}", response_model=List[FinanceHistoryRecord])
def get_expense_history(
    user_id: int,
    periodo: str = Query("1y", regex="^(1m|6m|1y|3y|5y)$"),
    db: Session = Depends(get_db),
):
    start = periodo_to_start_date(periodo)
    res = db.query(Expense).filter(Expense.user_id == user_id, Expense.date >= start).all()
    return group_by_month(res)

@router.get("/saving/{user_id}", response_model=List[FinanceHistoryRecord])
def get_saving_history(
    user_id: int,
    periodo: str = Query("1y", regex="^(1m|6m|1y|3y|5y)$"),
    db: Session = Depends(get_db),
):
    start = periodo_to_start_date(periodo)
    res = db.query(Saving).filter(Saving.user_id == user_id, Saving.date >= start).all()
    return group_by_month(res)

@router.get("/investment/{user_id}", response_model=List[FinanceHistoryRecord])
def get_investment_history(
    user_id: int,
    periodo: str = Query("1y", regex="^(1m|6m|1y|3y|5y)$"),
    db: Session = Depends(get_db),
):
    start = periodo_to_start_date(periodo)
    res = db.query(Investment).filter(Investment.user_id == user_id, Investment.date >= start).all()
    return group_by_month(res)

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
