"""
Dependencias de autenticación reutilizables para los endpoints protegidos.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import decode_access_token
from app.core.context import set_user_context

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    Decodifica el JWT y retorna el payload completo con validación de tipos.
    """
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        sub = payload.get("sub")
        if not sub:
            raise credentials_exc
        

        try:
            user_id = int(sub)
            payload["user_id"] = user_id
            set_user_context(user_id)
        except (ValueError, TypeError):
            print(f"DEBUG AUTH: sub no numérico: {sub}")
            raise credentials_exc
            
        return payload
    except JWTError as e:
        print(f"DEBUG AUTH: JWT Error: {str(e)}")
        raise credentials_exc
    except Exception as e:
        print(f"DEBUG AUTH: Error inesperado en validación: {str(e)}")
        raise credentials_exc


def require_role(*roles: str):
    """
    Fábrica de dependencias que restringe el acceso por rol.
    Uso: Depends(require_role("taller", "tecnico"))
    """
    async def _check(current=Depends(get_current_user)):
        if current["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para realizar esta acción",
            )
        return current
    return _check
