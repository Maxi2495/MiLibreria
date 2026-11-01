from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.usuarios import router as usuarios_router
from app.api.v1.espacios import router as espacios_router
from app.api.v1.catalogo import router as catalogo_router
from app.api.v1.ejemplares import router as ejemplares_router
from app.routers.auth import router as auth_router
from app.api.v1.prestamos import router as prestamos_router
from app.api.v1.lecturas import router as lecturas_router


app = FastAPI(
    title="BookNest API",
    description="API REST para el Sistema de Gestión de Bibliotecas Personales Físicas.",
    version="1.0.0"
)

# Configuración de CORS para desarrollo y frontend futuro
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de todos los routers del sistema
app.include_router(usuarios_router)
app.include_router(auth_router)
app.include_router(espacios_router, prefix="/api/v1")
app.include_router(catalogo_router, prefix="/api/v1")
app.include_router(ejemplares_router, prefix="/api/v1")
app.include_router(prestamos_router)
app.include_router(lecturas_router)


@app.get("/", tags=["General"])
def inicio():
    return {
        "sistema": "BookNest API",
        "estado": "En línea",
        "documentacion": "/docs"
    }


@app.get("/health", tags=["General"])
def verificar_estado():
    return {"status": "ok"}