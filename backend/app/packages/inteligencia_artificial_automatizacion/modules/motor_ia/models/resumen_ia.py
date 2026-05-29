from sqlalchemy import Column, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base


class ResumenIA(Base):
    __tablename__ = "resumen_ia"

    id = Column(Integer, primary_key=True)
    resumen = Column("Resumen", Text, nullable=False)
    ficha_tecnica = Column("FichaTecnica", JSON, nullable=True)
    recomendaciones_taller = Column(Text, nullable=True)
    motivo_rechazo = Column(Text, nullable=True)
    idEmergencia = Column(Integer, ForeignKey("emergencia.id"), nullable=False, index=True)

    emergencia = relationship("Emergencia", back_populates="resumen_ia")
