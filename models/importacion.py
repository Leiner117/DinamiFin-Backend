from sqlalchemy import Column, Integer, String, Float, Date
from db import Base

class Importacion(Base):
    __tablename__ = "importaciones"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)
    monto = Column(Float, nullable=False)
    categoria = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # ingresos, gastos, ahorros, inversiones, metas 