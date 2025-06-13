from fastapi import APIRouter
from .importacion import router as importacion_router
from .expenses import router as expenses_router
from .savings import router as savings_router
from .investments import router as investments_router
from routes.finance_history import router as finance_history_router
router = APIRouter()
router.include_router(importacion_router, prefix="/api/importacion", tags=["importacion"])
router.include_router(expenses_router)
router.include_router(savings_router)
router.include_router(investments_router)
router.include_router(finance_history_router)

__all__ = ['router']
