from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from db import get_db
from models.user import User
from models.expense_goal import ExpenseGoal
from models.saving_goal import SavingGoal
from models.investment_goal import InvestmentGoal
from schemas.user import PerfilUpdate
from routes.auth import get_current_user
from routes.auth import get_password_hash
from sqlalchemy import extract

router = APIRouter()

@router.get("/perfil")
def get_user_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "meta_gasto": get_meta(db, ExpenseGoal, current_user.id),
        "meta_ahorro": get_meta(db, SavingGoal, current_user.id),
        "meta_inversion": get_meta(db, InvestmentGoal, current_user.id),
    }

@router.put("/perfil")
def update_user_profile(
    perfil: PerfilUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cambios_credenciales = False

    if perfil.email:
        current_user.email = perfil.email
    if perfil.username and perfil.username != current_user.username:
        current_user.username = perfil.username
        cambios_credenciales = True
    if perfil.password:
        current_user.password = get_password_hash(perfil.password)
        cambios_credenciales = True

    db.commit()

    hoy = datetime.now().date()

    # Actualizar o insertar metas
    def upsert_meta(model, value):
        if value is None:
            return
        existente = db.query(model).filter_by(user_id=current_user.id, date=hoy).first()
        if existente:
            existente.value = value
        else:
            db.add(model(user_id=current_user.id, value=value, date=hoy))

    upsert_meta(ExpenseGoal, perfil.meta_gasto)
    upsert_meta(SavingGoal, perfil.meta_ahorro)
    upsert_meta(InvestmentGoal, perfil.meta_inversion)

    db.commit()

    return {
        "message": "Perfil actualizado correctamente",
        "logout_required": cambios_credenciales
    }


def get_meta(db: Session, model, user_id: int):
    hoy = datetime.now()
    actual = db.query(model).filter(
        model.user_id == user_id,
        extract("month", model.date) == hoy.month,
        extract("year", model.date) == hoy.year
    ).order_by(model.date.desc()).first()

    if actual:
        return actual.value

    anterior = db.query(model).filter(model.user_id == user_id)\
        .order_by(model.date.desc()).first()

    if anterior:
        return anterior.value

    return None

