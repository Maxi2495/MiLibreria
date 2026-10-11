import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("La variable DATABASE_URL no está configurada en el archivo .env")

# Si se conecta a Aiven, requiere configuración SSL para conexiones remotas
connect_args = {}
if "aivencloud.com" in DATABASE_URL:
    connect_args = {"ssl": {"ssl_mode": "REQUIRED"}}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()