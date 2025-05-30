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
class SavingGoal(Base):
    __tablename__ = 'saving_goals'
    __table_args__ = (
        PrimaryKeyConstraint('date', 'user_id'),
    )

    date = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    value = Column(Float, nullable=False)

    user = relationship("User", back_populates="saving_goals")