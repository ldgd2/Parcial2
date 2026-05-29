from sqlalchemy import Column, Integer, ForeignKey
from app.db.session import Base


class AsignacionTecnicoEmergencia(Base):
    __tablename__ = "asignacion_tecnico_emergencia"

    id = Column(Integer, primary_key=True)
    idTecnico = Column(Integer, ForeignKey("tecnico.id"), nullable=False, index=True)
    idEmergencia = Column(Integer, ForeignKey("emergencia.id"), nullable=False, index=True)
