import random
from datetime import date, timedelta
from db.db import SessionLocal, engine
from models import (
    Base, User, Income, Expense, Saving, Investment,
    ExpenseGoal, SavingGoal, InvestmentGoal
)
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    try:
        # Usuario único
        user = User(
            id=1,
            username="testuser",
            email="testuser@example.com",
            password=pwd_context.hash("a123")
        )
        db.merge(user)

        hoy = date.today()
        anios = 5  # Cambia la cantidad de años que desees
        meses_por_anio = 12

        for y in range(anios):
            for m in range(meses_por_anio):
                fecha = (hoy.replace(day=1) - timedelta(days=30 * (y * 12 + m)))
                year = fecha.year
                month = fecha.month
                fecha_mes = date(year, month, 1)

                # Solo un ingreso por mes
                ingreso = random.randint(900, 2500)
                db.merge(Income(date=fecha_mes, user_id=user.id, amount=ingreso))

                # Días disponibles en el mes
                dias_en_mes = (date(year + (month // 12), (month % 12) + 1, 1) - timedelta(days=1)).day
                dias_disponibles = list(range(1, dias_en_mes + 1))

                # Un gasto por día (varios días aleatorios en el mes)
                cantidad_gastos = random.randint(1, min(4, dias_en_mes))
                dias_gasto = random.sample(dias_disponibles, cantidad_gastos)
                for dia in dias_gasto:
                    fecha_gasto = date(year, month, dia)
                    gasto = random.randint(400, 1600)
                    categoria = random.choice(["general", "comida", "transporte", "salud", "ocio"])
                    db.merge(Expense(date=fecha_gasto, user_id=user.id, amount=gasto, category=categoria))

                # Un ahorro por día (días aleatorios, sin repetir con gastos)
                dias_restantes_ahorro = [d for d in dias_disponibles if d not in dias_gasto]
                cantidad_ahorros = random.randint(1, min(3, len(dias_restantes_ahorro))) if dias_restantes_ahorro else 0
                dias_ahorro = random.sample(dias_restantes_ahorro, cantidad_ahorros) if cantidad_ahorros > 0 else []
                for dia in dias_ahorro:
                    fecha_ahorro = date(year, month, dia)
                    ahorro = random.randint(100, 800)
                    db.merge(Saving(date=fecha_ahorro, user_id=user.id, amount=ahorro, category="general"))

                # Una inversión por día (días aleatorios, sin repetir con gastos ni ahorros)
                dias_restantes_inversion = [d for d in dias_disponibles if d not in dias_gasto and d not in dias_ahorro]
                cantidad_inversiones = random.randint(1, min(2, len(dias_restantes_inversion))) if dias_restantes_inversion else 0
                dias_inversion = random.sample(dias_restantes_inversion, cantidad_inversiones) if cantidad_inversiones > 0 else []
                for dia in dias_inversion:
                    fecha_inversion = date(year, month, dia)
                    inversion = random.randint(50, 400)
                    categoria_inv = random.choice(["fondos", "acciones", "cripto"])
                    db.merge(Investment(date=fecha_inversion, user_id=user.id, amount=inversion, category=categoria_inv))

                # Metas (una por mes)
                meta_gasto = random.randint(800, 1800)
                meta_ahorro = random.randint(200, 1000)
                meta_inversion = random.randint(100, 600)
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