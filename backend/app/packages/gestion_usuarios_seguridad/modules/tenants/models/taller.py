from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, Column, String, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship, joinedload
from app.db.generic_model import GenericModel
class Taller(GenericModel):
    __tablename__ = "taller"
    __table_args__ = {"schema": "public"}

    cod = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    direccion = Column(String(500), nullable=False)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    calificacion_promedio = Column(Float, nullable=False, default=5.0, server_default="5.0")
    estado = Column(String(20), nullable=False, default="ACTIVO")
    id_admin = Column(Integer, ForeignKey("public.usuario.id", name="fk_taller_admin", use_alter=True), nullable=True) # El admin principal
    plan_id = Column(Integer, ForeignKey("public.plan_suscripcion.id"), nullable=True)

    # Relaciones
    tecnicos = relationship("Tecnico", back_populates="taller")
    usuarios = relationship("Usuario", back_populates="taller", foreign_keys="Usuario.idTaller")
    emergencias = relationship("Emergencia", back_populates="taller", foreign_keys="Emergencia.idTaller")
    asignaciones = relationship("AsignacionEspecialidad", back_populates="taller")
    
    admin = relationship("Usuario", foreign_keys=[id_admin])
    plan = relationship("PlanSuscripcion", back_populates="talleres")
    sucursales = relationship("Sucursal", back_populates="taller")

    @classmethod
    async def get_by_cod(cls, db: AsyncSession, cod: str) -> Optional["Taller"]:
        result = await db.execute(select(cls).where(cls.cod == cod))
        return result.scalar_one_or_none()

    @classmethod
    async def get_with_especialidades(cls, db: AsyncSession, cod: str) -> Optional["Taller"]:
        from app.packages.gestion_emergencias_solicitudes.modules.auxilio_solicitudes.models.asignacion_especialidad import AsignacionEspecialidad
        stmt = (
            select(cls)
            .options(joinedload(cls.asignaciones).joinedload(AsignacionEspecialidad.especialidad))
            .where(cls.cod == cod)
        )
        result = await db.execute(stmt)
        return result.unique().scalar_one_or_none()

    @classmethod
    async def update_especialidades(cls, db: AsyncSession, cod: str, especialidades_ids: list[int]):
        from app.packages.gestion_emergencias_solicitudes.modules.auxilio_solicitudes.models.asignacion_especialidad import AsignacionEspecialidad
        await db.execute(
            delete(AsignacionEspecialidad).where(AsignacionEspecialidad.idTaller == cod)
        )
        for e_id in especialidades_ids:
            db.add(AsignacionEspecialidad(idTaller=cod, idEspecialidad=e_id))
        await db.flush()

    @classmethod
    async def get_by_admin_with_especialidades(cls, db: AsyncSession, admin_id: int) -> list["Taller"]:
        from app.packages.gestion_emergencias_solicitudes.modules.auxilio_solicitudes.models.asignacion_especialidad import AsignacionEspecialidad
        stmt = (
            select(cls)
            .options(joinedload(cls.asignaciones).joinedload(AsignacionEspecialidad.especialidad))
            .where(cls.id_admin == admin_id)
        )
        result = await db.execute(stmt)
        return list(result.scalars().unique().all())

    @classmethod
    async def get_activos(cls, db: AsyncSession) -> list["Taller"]:
        result = await db.execute(select(cls).where(cls.estado == "ACTIVO"))
        return list(result.scalars().all())

