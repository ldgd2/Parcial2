from sqlalchemy import Column, Integer, String
from app.db.session import Base


class Estado(Base):
    __tablename__ = "estado"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False, unique=True, index=True)
    descripcion = Column(String(255), nullable=False)
