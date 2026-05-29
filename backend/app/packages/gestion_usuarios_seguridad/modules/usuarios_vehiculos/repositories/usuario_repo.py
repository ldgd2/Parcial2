from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.db.repository import BaseRepository
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.usuario import Usuario

class UsuarioCreate(BaseModel):
    nombre: str
    apellido: str
    correo: str
    contrasena: str
    estado: str
    idTaller: Optional[str] = None

class UsuarioUpdate(BaseModel):
    pass

class UsuarioRepository(BaseRepository[Usuario, UsuarioCreate, UsuarioUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Usuario, db)

    async def get_by_correo(self, correo: str) -> Optional[Usuario]:
        result = await self.db.execute(select(Usuario).where(Usuario.correo == correo))
        return result.scalar_one_or_none()
