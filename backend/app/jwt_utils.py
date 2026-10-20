
import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from jwt import InvalidTokenError

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

if not JWT_SECRET_KEY:
    raise RuntimeError("Falta configurar JWT_SECRET_KEY en el archivo .env")


def crear_token_acceso(usuario_id: int) -> str:
    ahora = datetime.now(timezone.utc)

    datos = {
        "sub": str(usuario_id),
        "iat": ahora,
        "exp": ahora + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    return jwt.encode(datos, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verificar_token_acceso(token: str) -> int | None:
    try:
        datos = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "iat", "exp"]},
        )
        return int(datos["sub"])
    except (InvalidTokenError, ValueError, TypeError):
        return None
