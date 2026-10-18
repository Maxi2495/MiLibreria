
from fastapi import FastAPI
from app.routers.usuarios import router as usuarios_router

app = FastAPI(
    title="BookNest API",
    description="API REST para el Sistema de Gestión de Bibliotecas Personales",
    version="0.1.0"
)


@app.get("/")
def inicio():
    return {
        "mensaje": "Bienvenido a la API de BookNest"
    }


@app.get("/health")
def verificar_estado():
    return {
        "status": "ok"
    }

app.include_router(usuarios_router)