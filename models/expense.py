from datetime import date
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    ForeignKey,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import relationship, declarative_base
from . import Base
class Expense(Base):
    __tablename__ = 'expenses'
    __table_args__ = (
        PrimaryKeyConstraint('date', 'user_id'),
    )

    date = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=True)

    user = relationship("User", back_populates="expenses")