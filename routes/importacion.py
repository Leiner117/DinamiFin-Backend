from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import json
from datetime import datetime
from sqlalchemy.orm import Session
from db import get_db
from models.importacion import Importacion

router = APIRouter()

@router.post("/importar")
async def importar_datos(
    file: UploadFile = File(...),
    tipo: str = Form(...),
    datos: str = Form(...)
):
    try:
        # Convertir los datos de string JSON a lista de diccionarios
        datos_lista = json.loads(datos)
        
        # Obtener la sesión de la base de datos
        db = next(get_db())
        
        # Crear registros en la base de datos
        for dato in datos_lista:
            nueva_importacion = Importacion(
                fecha=datetime.strptime(dato['fecha'], '%Y-%m-%d'),
                monto=float(dato['monto']),
                categoria=dato['categoria'],
                tipo=tipo
            )
            db.add(nueva_importacion)
        
        # Guardar los cambios
        db.commit()
        
        return {
            "message": "Datos importados exitosamente",
            "registros_importados": len(datos_lista)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error al importar los datos: {str(e)}"
        ) 