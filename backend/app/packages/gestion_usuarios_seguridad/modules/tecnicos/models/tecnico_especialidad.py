from sqlalchemy import Column, Integer, ForeignKey
from app.db.generic_model import GenericModel
class TecnicoEspecialidad(GenericModel):
    __tablename__ = "tecnico_especialidad"
    __table_args__ = {"schema": "public"}

    idTecnico = Column(Integer, ForeignKey("public.tecnico.id"), primary_key=True)
    idEspecialidad = Column(Integer, ForeignKey("public.especialidad.id"), primary_key=True)
