from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base

class Bitacora(Base):
    __tablename__ = "bitacora"

    id = Column(Integer, primary_key=True, index=True)
    idUsuario = Column(Integer, nullable=True) # ID de Usuario o Cliente (sin FK estricta para evitar conflictos)
    accion = Column(String(50), nullable=False)  # LOGIN, INSERT, UPDATE, DELETE
    tabla = Column(String(100), nullable=True)
    registro_id = Column(String(100), nullable=True)
    detalles = Column(JSON, nullable=True)  # { "antes": {...}, "despues": {...} }
    ip = Column(String(45), nullable=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Bitacora(id={self.id}, accion='{self.accion}', tabla='{self.tabla}')>"
