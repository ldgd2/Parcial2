from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class Evidencia(Base):
    __tablename__ = "evidencia"

    id = Column(Integer, primary_key=True)
    direccion = Column(String(500), nullable=False)
    idEmergencia = Column(Integer, ForeignKey("emergencia.id"), nullable=False, index=True)

    emergencia = relationship("Emergencia", back_populates="evidencias")
