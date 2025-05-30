from sqlalchemy.orm import declarative_base

# Base para todos los modelos
Base = declarative_base()

# Importar modelos para que sean visibles al hacer "import models"
from .user import User
from .income import Income
from .expense import Expense
from .saving import Saving
from .investment import Investment
from .expense_goal import ExpenseGoal
from .saving_goal import SavingGoal
from .investment_goal import InvestmentGoal
