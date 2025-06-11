from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field, validator
from enum import Enum

from db.db import get_db
from models.saving import Saving

router = APIRouter(
    prefix="/datos/ahorros",
    tags=["ahorros"]
)

class SavingCategory(str, Enum):
    FONDO_EMERGENCIA = "fondo de emergencia"
    JUBILACION = "jubilación"
    VACACIONES = "vacaciones"
    MANTENIMIENTO = "mantenimiento"
    OTROS = "otros"

class SavingCreate(BaseModel):
    amount: float = Field(..., gt=0, description="El monto debe ser mayor que 0")
    category: SavingCategory
    income_date: date

    @validator('income_date')
    def validate_date_format(cls, v):
        if not isinstance(v, date):
            try:
                # Intentar convertir la cadena a fecha
                v = date.fromisoformat(str(v))
            except ValueError:
                raise ValueError("La fecha debe estar en formato YYYY-MM-DD")
        return v

class SavingUpdate(BaseModel):
    amount: float = Field(..., gt=0, description="El monto debe ser mayor que 0")
    category: Optional[SavingCategory] = None

@router.get("/{user_id}", response_model=List[dict])
def get_savings(user_id: int, db: Session = Depends(get_db)):
    try:
        savings = db.query(Saving).filter(
            Saving.user_id == user_id
        ).all()
        return [
            {
                "date": saving.date,
                "amount": saving.amount,
                "category": saving.category
            }
            for saving in savings
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}/{date}", response_model=dict)
def get_saving_by_date(user_id: int, date: date, db: Session = Depends(get_db)):
    try:
        saving = db.query(Saving).filter(
            Saving.user_id == user_id,
            Saving.date == date
        ).first()
        
        if not saving:
            raise HTTPException(status_code=404, detail="Ahorro no encontrado")
            
        return {
            "date": saving.date,
            "amount": saving.amount,
            "category": saving.category
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{user_id}")
def create_saving(user_id: int, saving: SavingCreate, db: Session = Depends(get_db)):
    try:
        existing_saving = db.query(Saving).filter(
            Saving.user_id == user_id,
            Saving.date == saving.income_date
        ).first()
        
        if existing_saving:
            raise HTTPException(
                status_code=400,
                detail="Ya existe un ahorro registrado para esta fecha. Use el endpoint PUT para actualizarlo."
            )

        new_saving = Saving(
            user_id=user_id,
            amount=saving.amount,
            category=saving.category,
            date=saving.income_date
        )
        db.add(new_saving)
        db.commit()
        db.refresh(new_saving)
        return {"message": "Ahorro creado exitosamente", "data": new_saving}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{user_id}/{date}")
def update_saving(user_id: int, date: date, saving: SavingUpdate, db: Session = Depends(get_db)):
    try:
        saving_db = db.query(Saving).filter(
            Saving.user_id == user_id,
            Saving.date == date
        ).first()
        
        if not saving_db:
            raise HTTPException(status_code=404, detail="Ahorro no encontrado")
        
        saving_db.amount = saving.amount
        if saving.category is not None:
            saving_db.category = saving.category
            
        db.commit()
        return {"message": "Ahorro actualizado exitosamente", "data": saving_db}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}/{date}")
def delete_saving(user_id: int, date: date, db: Session = Depends(get_db)):
    try:
        saving = db.query(Saving).filter(
            Saving.user_id == user_id,
            Saving.date == date
        ).first()
        
        if not saving:
            raise HTTPException(status_code=404, detail="Ahorro no encontrado")
        
        db.delete(saving)
        db.commit()
        return {"message": "Ahorro eliminado exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) 