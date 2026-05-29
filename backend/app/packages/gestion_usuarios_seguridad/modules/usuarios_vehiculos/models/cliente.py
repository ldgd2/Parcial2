from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class Cliente(Base):
    __tablename__ = "cliente"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    correo = Column(String(255), nullable=False, unique=True, index=True)
    contrasena = Column("contraseña", String(255), nullable=False)
    estado = Column(String(20), nullable=False, server_default="ACTIVO", default="ACTIVO")
    fcm_token = Column(String(512), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)

    # Relaciones
    vehiculos = relationship("Vehiculo", back_populates="cliente")
    emergencias = relationship("Emergencia", back_populates="cliente")
