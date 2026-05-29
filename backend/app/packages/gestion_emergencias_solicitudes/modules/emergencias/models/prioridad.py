from sqlalchemy import Column, Integer, String
from app.db.session import Base


class Prioridad(Base):
    __tablename__ = "prioridad"

    id = Column(Integer, primary_key=True)
    descripcion = Column(String(255), nullable=False)
