from fastapi import APIRouter
from .importacion import router as importacion_router

router = APIRouter()
router.include_router(importacion_router, prefix="/api/importacion", tags=["importacion"])
