from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    apellido = Column(String(255), nullable=False)
    correo = Column(String(255), nullable=False, unique=True, index=True)
    contrasena = Column("contraseña", String(255), nullable=False)
    estado = Column(String(20), nullable=False, server_default="ACTIVO", default="ACTIVO")
    fcm_token = Column(String(512), nullable=True)
    idTaller = Column(String(10), ForeignKey("taller.cod"), nullable=False, index=True)

    # Relaciones
    taller = relationship("Taller", back_populates="usuarios", foreign_keys=[idTaller])
