from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, conint
from datetime import date
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.db import get_db
from models.user import User
from models.expense_goal import ExpenseGoal
from models.saving_goal import SavingGoal
from models.investment_goal import InvestmentGoal
import re

SECRET_KEY = "dinamifin-secret"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

router = APIRouter()

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str | None = None
    password: str
    meta_gasto: conint(ge=0, le=100) | None = 0
    meta_ahorro: conint(ge=0, le=100) | None = 0
    meta_inversion: conint(ge=0, le=100) | None = 0

    @classmethod
    def validate(cls, values):
        password = values.get('password')
        username = values.get('username')

        if username and len(username) > 50:
            raise ValueError("El nombre de usuario no debe superar los 50 caracteres")

        pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{10,}$'
        if not re.match(pattern, password):
            raise ValueError("La contraseña debe tener al menos 10 caracteres, una letra, un número y un símbolo")

        return values

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if data.meta_gasto + data.meta_ahorro + data.meta_inversion > 100:
        raise HTTPException(status_code=400, detail="La suma de metas no puede superar el 100%")

    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    hashed_password = pwd_context.hash(data.password)
    user = User(email=data.email, username=data.username or data.email, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)

    today = date.today()
    if data.meta_gasto:
        db.add(ExpenseGoal(user_id=user.id, value=data.meta_gasto, date=today))
    if data.meta_ahorro:
        db.add(SavingGoal(user_id=user.id, value=data.meta_ahorro, date=today))
    if data.meta_inversion:
        db.add(InvestmentGoal(user_id=user.id, value=data.meta_inversion, date=today))
    db.commit()

    return {"message": "Usuario registrado exitosamente"}

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not pwd_context.verify(data.password, user.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token_data = {"sub": user.email, "user_id": user.id}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/dashboard")
def get_dashboard(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username
    }

