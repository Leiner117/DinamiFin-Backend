from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
import csv
import io
from datetime import datetime
from db import get_db
from models import Income, Expense, Saving, Investment, ExpenseGoal, SavingGoal, InvestmentGoal

router = APIRouter()

# Mapeo de tipos de registros a sus modelos y columnas requeridas
TIPOS_REGISTROS = {
    'expense': {
        'modelo': Expense,
        'columnas': {'date', 'amount', 'category'},
        'tiene_categoria': True
    },
    'income': {
        'modelo': Income,
        'columnas': {'date', 'amount'},
        'tiene_categoria': False
    },
    'saving': {
        'modelo': Saving,
        'columnas': {'date', 'amount', 'category'},
        'tiene_categoria': True
    },
    'investment': {
        'modelo': Investment,
        'columnas': {'date', 'amount', 'category'},
        'tiene_categoria': True
    }
}

# Mapeo de tipos de metas
TIPOS_METAS = {
    'expense_goal': {
        'modelo': ExpenseGoal,
        'columnas': {'date', 'value'},
        'tiene_categoria': False
    },
    'saving_goal': {
        'modelo': SavingGoal,
        'columnas': {'date', 'value'},
        'tiene_categoria': False
    },
    'investment_goal': {
        'modelo': InvestmentGoal,
        'columnas': {'date', 'value'},
        'tiene_categoria': False
    }
}

def validar_fecha(fecha_str):
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        return None

def validar_monto(monto_str):
    try:
        # Reemplazar coma por punto y eliminar espacios
        monto_str = monto_str.replace(',', '.').strip()
        monto = float(monto_str)
        return monto if monto >= 0 else None
    except (ValueError, TypeError):
        return None

def validar_categoria(categoria):
    return categoria.strip() if categoria else None

@router.post("/importar")
async def importar_csv(
    file: UploadFile = File(...),
    tipo: str = Form(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    # Validar tipo de registro
    if tipo not in {**TIPOS_REGISTROS, **TIPOS_METAS}:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo '{tipo}' no soportado. Tipos válidos: {', '.join({**TIPOS_REGISTROS, **TIPOS_METAS}.keys())}"
        )

    # Obtener configuración del tipo
    config = TIPOS_REGISTROS.get(tipo) or TIPOS_METAS.get(tipo)
    
    try:
        contenido = await file.read()
        contenido_str = contenido.decode('utf-8')
        csv_file = io.StringIO(contenido_str)
        reader = csv.DictReader(csv_file)

        # Validar columnas requeridas
        if not config['columnas'].issubset(reader.fieldnames):
            raise HTTPException(
                status_code=400,
                detail=f"El archivo CSV debe contener las columnas: {', '.join(config['columnas'])}"
            )

        errores = []
        registros_validos = []

        for idx, row in enumerate(reader, 1):
            # Validar fecha
            fecha = validar_fecha(row['date'])
            if not fecha:
                errores.append(f"Línea {idx}: Fecha inválida (formato YYYY-MM-DD)")
                continue

            # Validar monto (amount o value según el tipo)
            campo_monto = 'value' if tipo in TIPOS_METAS else 'amount'
            monto = validar_monto(row[campo_monto])
            if monto is None:
                errores.append(f"Línea {idx}: Monto inválido")
                continue

            # Validar categoría si es necesario
            categoria = None
            if config['tiene_categoria']:
                categoria = validar_categoria(row['category'])
                if not categoria:
                    errores.append(f"Línea {idx}: Categoría inválida")
                    continue

            registros_validos.append({
                'fecha': fecha,
                'monto': monto,
                'categoria': categoria
            })

        if errores:
            raise HTTPException(
                status_code=400,
                detail={"mensaje": "Errores en el CSV", "errores": errores}
            )

        # Insertar registros válidos en la base de datos
        for registro in registros_validos:
            if tipo in TIPOS_METAS:
                nuevo = config['modelo'](
                    user_id=user_id,
                    date=registro['fecha'],
                    value=registro['monto']
                )
            else:
                nuevo = config['modelo'](
                    user_id=user_id,
                    date=registro['fecha'],
                    amount=registro['monto'],
                    category=registro['categoria'] if config['tiene_categoria'] else None
                )
            db.add(nuevo)

        db.commit()
        return {
            "mensaje": f"{len(registros_validos)} registros importados correctamente",
            "tipo": tipo,
            "registros_importados": len(registros_validos)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
