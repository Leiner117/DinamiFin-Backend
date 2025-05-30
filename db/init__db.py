from db import Base, engine
from models import User, Income, Expense, Saving, Investment, ExpenseGoal, SavingGoal, InvestmentGoal

Base.metadata.create_all(bind=engine)
