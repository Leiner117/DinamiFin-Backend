import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router as api_router
from db import Base, engine 

app = FastAPI()

# Crear la base de datos al arrancar si no existe
@app.on_event("startup")
def startup_event():
    print("Verificando si las tablas existen...")
    Base.metadata.create_all(bind=engine)
    print("Tablas verificadas o creadas correctamente.")

# Incluir todas las rutas de la API
#app.include_router(api_router)

# Middleware CORS (ajustar en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes (inseguro en prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta raíz para prueba
@app.get("/")
async def root():
    return {"message": "API FUNCIONANDO"}
