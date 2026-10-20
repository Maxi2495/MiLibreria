
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, TokenResponse
from app.security import verificar_password
from app.jwt_utils import crear_token_acceso
from app.dependencies import get_current_user
from app.schemas.usuario import UsuarioRespuesta

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse)
def iniciar_sesion(
    datos: LoginRequest,
    db: Session = Depends(get_db)
):
    # Buscar al usuario por correo electrónico
    usuario = (
        db.query(Usuario)
        .filter(Usuario.email == str(datos.email))
        .first()
    )

    # Verificar que exista y que la contraseña sea correcta
    if usuario is None or not verificar_password(
        datos.password, usuario.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Impedir el acceso a cuentas inactivas
    if usuario.estado != "ACTIVA":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta no está activa",
        )

    # Generar el token JWT
    token = crear_token_acceso(usuario.id)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
    )


@router.get("/me", response_model=UsuarioRespuesta)
def obtener_mi_perfil(
    usuario_actual: Usuario = Depends(get_current_user)
):
    return usuario_actual
