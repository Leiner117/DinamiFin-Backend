import random
from datetime import date, timedelta
from db.db import SessionLocal, engine
from models import (
    Base, User, Income, Expense, Saving, Investment,
    ExpenseGoal, SavingGoal, InvestmentGoal
)

# Asegura que las tablas existan (puedes omitir si ya las migraste)
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    try:
        # Crear usuario de prueba
        user = User(
            id=1,
            username="testuser",
            email="testuser@example.com",
            password="a123"
        )
        db.merge(user)  # merge evita duplicados por PK

        hoy = date.today()
        for i in range(12):
            fecha = (hoy.replace(day=1) - timedelta(days=30 * i))
            year = fecha.year
            month = fecha.month
            fecha_mes = date(year, month, 1)

            ingreso = 1200 + random.randint(-200, 400)
            gasto = 900 + random.randint(-100, 250)
            ahorro = ingreso - gasto + random.randint(-50, 100)
            inversion = 150 + random.randint(-30, 80)

            meta_gasto = gasto - random.randint(0, 50)
            meta_ahorro = ahorro + random.randint(0, 50)
            meta_inversion = inversion + random.randint(0, 30)

            db.merge(Income(date=fecha_mes, user_id=user.id, amount=ingreso))
            db.merge(Expense(date=fecha_mes, user_id=user.id, amount=gasto, category="general"))
            db.merge(Saving(date=fecha_mes, user_id=user.id, amount=ahorro, category="general"))
            db.merge(Investment(date=fecha_mes, user_id=user.id, amount=inversion, category="fondos"))

            db.merge(ExpenseGoal(date=fecha_mes, user_id=user.id, value=meta_gasto))
            db.merge(SavingGoal(date=fecha_mes, user_id=user.id, value=meta_ahorro))
            db.merge(InvestmentGoal(date=fecha_mes, user_id=user.id, value=meta_inversion))

        db.commit()
        print("Datos de prueba cargados correctamente.\n")

        # ---------- Imprimir los datos de la base -----------
        print("Usuarios:")
        for u in db.query(User).all():
            print(vars(u))

        print("\nIngresos (Income):")
        for r in db.query(Income).all():
            print(vars(r))

        print("\nGastos (Expense):")
        for r in db.query(Expense).all():
            print(vars(r))

        print("\nAhorros (Saving):")
        for r in db.query(Saving).all():
            print(vars(r))

        print("\nInversiones (Investment):")
        for r in db.query(Investment).all():
            print(vars(r))

        print("\nMetas de Gasto (ExpenseGoal):")
        for r in db.query(ExpenseGoal).all():
            print(vars(r))

        print("\nMetas de Ahorro (SavingGoal):")
        for r in db.query(SavingGoal).all():
            print(vars(r))

        print("\nMetas de Inversión (InvestmentGoal):")
        for r in db.query(InvestmentGoal).all():
            print(vars(r))

        print("\nFin de datos.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
