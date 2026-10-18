from fastapi import FastAPI
from app.routers.usuarios import router as usuarios_router
from app.api.v1.espacios import router as espacios_router

app = FastAPI(
    title="BookNest API",
    description="API REST para el Sistema de Gestión de Bibliotecas Personales Físicas.",
    version="1.0.0"
)

# Endpoint raíz
@app.get("/", tags=["General"])
def inicio():
    return {
        "sistema": "BookNest API",
        "estado": "En línea",
        "documentacion": "/docs"
    }

# Endpoint de chequeo de salud
@app.get("/health", tags=["General"])
def verificar_estado():
    return {
        "status": "ok"
    }

# Registrar los módulos de la aplicación
app.include_router(usuarios_router)
app.include_router(espacios_router, prefix="/api/v1")