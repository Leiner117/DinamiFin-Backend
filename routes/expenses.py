from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field, validator
from enum import Enum

from db.db import get_db
from models.expense import Expense

router = APIRouter(
    prefix="/datos/gastos",
    tags=["gastos"]
)

class ExpenseCategory(str, Enum):
    VIVIENDA = "vivienda"
    ALIMENTACION = "alimentación"
    TRANSPORTE = "transporte"
    SALUD = "salud"
    EDUCACION = "educación"
    ENTRETENIMIENTO = "entretenimiento"
    ROPA = "ropa"
    OTROS = "otros"

class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0, description="El monto debe ser mayor que 0")
    category: ExpenseCategory
    expense_date: date

    @validator('expense_date')
    def validate_date_format(cls, v):
        if not isinstance(v, date):
            try:
                # Intentar convertir la cadena a fecha
                v = date.fromisoformat(str(v))
            except ValueError:
                raise ValueError("La fecha debe estar en formato YYYY-MM-DD")
        return v

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0, description="El monto debe ser mayor que 0")
    category: Optional[ExpenseCategory] = None

@router.get("/{user_id}", response_model=List[dict])
def get_expenses(user_id: int, db: Session = Depends(get_db)):
    try:
        expenses = db.query(Expense).filter(
            Expense.user_id == user_id
        ).all()
        return [
            {
                "date": expense.date,
                "amount": expense.amount,
                "category": expense.category
            }
            for expense in expenses
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}/{date}", response_model=dict)
def get_expense_by_date(user_id: int, date: date, db: Session = Depends(get_db)):
    try:
        expense = db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.date == date
        ).first()
        
        if not expense:
            raise HTTPException(status_code=404, detail="Gasto no encontrado")
            
        return {
            "date": expense.date,
            "amount": expense.amount,
            "category": expense.category
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{user_id}")
def create_expense(user_id: int, expense: ExpenseCreate, db: Session = Depends(get_db)):
    try:
        existing_expense = db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.date == expense.expense_date
        ).first()
        
        if existing_expense:
            raise HTTPException(
                status_code=400,
                detail="Ya existe un gasto registrado para esta fecha. Use el endpoint PUT para actualizarlo."
            )

        new_expense = Expense(
            user_id=user_id,
            amount=expense.amount,
            category=expense.category,
            date=expense.expense_date
        )
        db.add(new_expense)
        db.commit()
        db.refresh(new_expense)
        return {"message": "Gasto creado exitosamente", "data": new_expense}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{user_id}/{date}")
def update_expense(user_id: int, date: date, expense: ExpenseUpdate, db: Session = Depends(get_db)):
    try:
        expense_db = db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.date == date
        ).first()
        
        if not expense_db:
            raise HTTPException(status_code=404, detail="Gasto no encontrado")
        
        if expense.amount is not None:
            expense_db.amount = expense.amount
        if expense.category is not None:
            expense_db.category = expense.category
            
        db.commit()
        return {"message": "Gasto actualizado exitosamente", "data": expense_db}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}/{date}")
def delete_expense(user_id: int, date: date, db: Session = Depends(get_db)):
    try:
        expense = db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.date == date
        ).first()
        
        if not expense:
            raise HTTPException(status_code=404, detail="Gasto no encontrado")
        
        db.delete(expense)
        db.commit()
        return {"message": "Gasto eliminado exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) 