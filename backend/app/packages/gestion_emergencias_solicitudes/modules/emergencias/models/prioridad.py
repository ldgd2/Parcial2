from sqlalchemy import Column, Integer, String
from app.db.generic_model import GenericModel
class Prioridad(GenericModel):
    __tablename__ = "prioridad"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    descripcion = Column(String(255), nullable=False)
