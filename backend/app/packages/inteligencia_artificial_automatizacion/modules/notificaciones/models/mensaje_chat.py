from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base
import datetime

class MensajeChat(Base):
    __tablename__ = "mensajes_chat"

    id = Column(Integer, primary_key=True, index=True)
    idEmergencia = Column(Integer, ForeignKey("emergencia.id"), nullable=False)
    remitente_id = Column(Integer, nullable=False) # ID de Cliente o Usuario
    rol_remitente = Column(String(20), nullable=False) # "cliente", "tecnico", "admin"
    contenido = Column(Text, nullable=True)
    imagen_url = Column(String(255), nullable=True)
    audio_url = Column(String(255), nullable=True)
    fecha_envio = Column(DateTime, default=datetime.datetime.now)

    # Relaciones
    emergencia = relationship("Emergencia", back_populates="mensajes_chat")
