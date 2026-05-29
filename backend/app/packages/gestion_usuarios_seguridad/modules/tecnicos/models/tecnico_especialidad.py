from sqlalchemy import Column, Integer, ForeignKey
from app.db.session import Base

class TecnicoEspecialidad(Base):
    __tablename__ = "tecnico_especialidad"

    idTecnico = Column(Integer, ForeignKey("tecnico.id"), primary_key=True)
    idEspecialidad = Column(Integer, ForeignKey("especialidad.id"), primary_key=True)
