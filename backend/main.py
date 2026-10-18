from fastapi import FastAPI
from app.api.v1.espacios import router as espacios_router

app = FastAPI(
    title="BookNest API",
    description="API REST para la gestión y trazabilidad de bibliotecas personales físicas.",
    version="1.0.0"
)

# Conectar rutas del módulo de espacios
app.include_router(espacios_router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "sistema": "BookNest API",
        "estado": "En línea",
        "documentacion": "/docs"
    }