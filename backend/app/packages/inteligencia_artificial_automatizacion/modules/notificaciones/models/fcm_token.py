from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from app.db.session import Base

class FCMToken(Base):
    __tablename__ = "fcm_token"

    id = Column(Integer, primary_key=True, index=True)
    idUsuario = Column(Integer, ForeignKey("usuario.id"), nullable=True, index=True)
    idCliente = Column(Integer, ForeignKey("cliente.id"), nullable=True, index=True)
    token = Column(String(512), nullable=False, unique=True)
    dispositivo = Column(String(50), nullable=True) # ej: android, ios, web
    fecha_registro = Column(DateTime, default=datetime.datetime.utcnow)

    # Relaciones
    usuario = relationship("Usuario", backref="fcm_tokens")
    cliente = relationship("Cliente", backref="fcm_tokens")
