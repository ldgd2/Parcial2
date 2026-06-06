from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.generic_model import GenericModel

class Permiso(GenericModel):
    __tablename__ = "permiso"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(100), nullable=False, unique=True) # ej. VER_REPORTES, CREAR_SUCURSAL
    descripcion = Column(String(255), nullable=True)

    # Relaciones
    planes = relationship("PlanSuscripcion", secondary="public.plan_permiso", back_populates="permisos")
    roles = relationship("Rol", secondary="public.rol_permiso", back_populates="permisos")

class Rol(GenericModel):
    __tablename__ = "rol"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False, unique=True) # ADMIN_TALLER, MECANICO, CLIENTE
    
    permisos = relationship("Permiso", secondary="public.rol_permiso", back_populates="roles")


class PlanPermiso(GenericModel):
    __tablename__ = "plan_permiso"
    __table_args__ = {"schema": "public"}

    id_plan = Column(Integer, ForeignKey("public.plan_suscripcion.id"), primary_key=True)
    id_permiso = Column(Integer, ForeignKey("public.permiso.id"), primary_key=True)


class RolPermiso(GenericModel):
    __tablename__ = "rol_permiso"
    __table_args__ = {"schema": "public"}

    id_rol = Column(Integer, ForeignKey("public.rol.id"), primary_key=True)
    id_permiso = Column(Integer, ForeignKey("public.permiso.id"), primary_key=True)
