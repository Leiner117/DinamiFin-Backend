from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field, validator
from enum import Enum

from db.db import get_db
from models.investment import Investment

router = APIRouter(
    prefix="/datos/inversiones",
    tags=["inversiones"]
)

class InvestmentCategory(str, Enum):
    FONDO_INVERSION = "fondo de inversión"
    ACCIONES = "acciones"
    BIENES_RAICES = "bienes raíces"
    CRIPTO = "cripto"
    NEGOCIO = "negocio"
    OTROS = "otros"

class InvestmentCreate(BaseModel):
    amount: float = Field(..., gt=0, description="El monto debe ser mayor que 0")
    category: InvestmentCategory
    investment_date: date

    @validator('investment_date')
    def validate_date_format(cls, v):
        if not isinstance(v, date):
            try:
                v = date.fromisoformat(str(v))
            except ValueError:
                raise ValueError("La fecha debe estar en formato YYYY-MM-DD")
        return v

class InvestmentUpdate(BaseModel):
    amount: float = Field(..., gt=0, description="El monto debe ser mayor que 0")
    category: Optional[InvestmentCategory] = None

@router.get("/{user_id}", response_model=List[dict])
def get_investments(user_id: int, db: Session = Depends(get_db)):
    try:
        investments = db.query(Investment).filter(
            Investment.user_id == user_id
        ).all()
        return [
            {
                "date": investment.date,
                "amount": investment.amount,
                "category": investment.category
            }
            for investment in investments
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}/{date}", response_model=dict)
def get_investment_by_date(user_id: int, date: date, db: Session = Depends(get_db)):
    try:
        investment = db.query(Investment).filter(
            Investment.user_id == user_id,
            Investment.date == date
        ).first()
        
        if not investment:
            raise HTTPException(status_code=404, detail="Inversión no encontrada")
            
        return {
            "date": investment.date,
            "amount": investment.amount,
            "category": investment.category
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{user_id}")
def create_investment(user_id: int, investment: InvestmentCreate, db: Session = Depends(get_db)):
    try:
        existing_investment = db.query(Investment).filter(
            Investment.user_id == user_id,
            Investment.date == investment.investment_date
        ).first()
        
        if existing_investment:
            raise HTTPException(
                status_code=400,
                detail="Ya existe una inversión registrada para esta fecha. Use el endpoint PUT para actualizarla."
            )

        new_investment = Investment(
            user_id=user_id,
            amount=investment.amount,
            category=investment.category,
            date=investment.investment_date
        )
        db.add(new_investment)
        db.commit()
        db.refresh(new_investment)
        return {"message": "Inversión creada exitosamente", "data": new_investment}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{user_id}/{date}")
def update_investment(user_id: int, date: date, investment: InvestmentUpdate, db: Session = Depends(get_db)):
    try:
        investment_db = db.query(Investment).filter(
            Investment.user_id == user_id,
            Investment.date == date
        ).first()
        
        if not investment_db:
            raise HTTPException(status_code=404, detail="Inversión no encontrada")
        
        investment_db.amount = investment.amount
        if investment.category is not None:
            investment_db.category = investment.category
            
        db.commit()
        return {"message": "Inversión actualizada exitosamente", "data": investment_db}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}/{date}")
def delete_investment(user_id: int, date: date, db: Session = Depends(get_db)):
    try:
        investment = db.query(Investment).filter(
            Investment.user_id == user_id,
            Investment.date == date
        ).first()
        
        if not investment:
            raise HTTPException(status_code=404, detail="Inversión no encontrada")
        
        db.delete(investment)
        db.commit()
        return {"message": "Inversión eliminada exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) 
