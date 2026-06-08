from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship, selectinload
from app.db.generic_model import GenericModel
class Tecnico(GenericModel):
    __tablename__ = "tecnico"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    correo = Column(String(255), nullable=False, unique=True, index=True)
    contrasena = Column("contraseña", String(255), nullable=False)
    telefono = Column(String(20), nullable=False)
    estado = Column(String(20), nullable=False, server_default="ACTIVO", default="ACTIVO")
    idTaller = Column(String(10), ForeignKey("public.taller.cod"), nullable=False, index=True)
    idSucursal = Column(Integer, ForeignKey("public.sucursal.id"), nullable=True, index=True)
    calificacion_promedio = Column(Float, nullable=False, default=5.0, server_default="5.0")

    # Relaciones
    taller = relationship("Taller", back_populates="tecnicos")
    sucursal = relationship("Sucursal")
    especialidades = relationship("Especialidad", secondary="public.tecnico_especialidad", back_populates="tecnicos")
    emergencias_asignadas = relationship("Emergencia", secondary="public.asignacion_tecnico_emergencia", back_populates="tecnicos_asignados")

    @classmethod
    async def get_by_correo(cls, db: AsyncSession, correo: str) -> Optional["Tecnico"]:
        result = await db.execute(select(cls).where(cls.correo == correo))
        return result.scalar_one_or_none()

    @classmethod
    async def get_with_especialidades(cls, db: AsyncSession, id: int) -> Optional["Tecnico"]:
        stmt = select(cls).options(selectinload(cls.especialidades)).where(cls.id == id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    @classmethod
    async def get_by_taller_with_especialidades(cls, db: AsyncSession, idTaller: str, idSucursal: Optional[int] = None) -> list["Tecnico"]:
        stmt = select(cls).options(selectinload(cls.especialidades)).where(cls.idTaller == idTaller)
        if idSucursal is not None:
            stmt = stmt.where(cls.idSucursal == idSucursal)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def update_especialidades(cls, db: AsyncSession, tecnico_id: int, especialidades_ids: list[int]):
        from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.tecnico_especialidad import TecnicoEspecialidad
        # 1. Eliminar asignaciones actuales
        await db.execute(
            delete(TecnicoEspecialidad).where(TecnicoEspecialidad.idTecnico == tecnico_id)
        )
        # 2. Insertar nuevas
        for esp_id in especialidades_ids:
            db.add(TecnicoEspecialidad(idTecnico=tecnico_id, idEspecialidad=esp_id))
        await db.flush()

