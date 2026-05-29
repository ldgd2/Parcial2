from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class Vehiculo(Base):
    __tablename__ = "vehiculo"

    placa = Column(String(20), primary_key=True, index=True)
    marca = Column(String(100), nullable=False)
    modelo = Column(String(100), nullable=False)
    anio = Column("año", Integer, nullable=False)
    idCliente = Column(Integer, ForeignKey("cliente.id"), nullable=False, index=True)

    # Relaciones
    cliente = relationship("Cliente", back_populates="vehiculos")
    emergencias = relationship("Emergencia", back_populates="vehiculo")
