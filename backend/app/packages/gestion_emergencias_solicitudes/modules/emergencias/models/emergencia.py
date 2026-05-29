from sqlalchemy import Column, Integer, String, Text, Date, Time, ForeignKey, func, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base


class Emergencia(Base):
    __tablename__ = "emergencia"

    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(500), nullable=False)
    texto_adicional = Column("textoAdicional", Text, nullable=True)
    direccion = Column(String(500), nullable=False)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    es_valida = Column(Boolean, default=True, server_default="true")
    fecha = Column(Date, nullable=False, server_default=func.current_date())
    hora = Column(Time, nullable=False)

    # Claves foráneas (idTaller es nullable ahora hasta que alguien la tome)
    idTaller = Column(String(10), ForeignKey("taller.cod"), nullable=True, index=True)
    idPrioridad = Column(Integer, ForeignKey("prioridad.id"), nullable=False)
    idCategoria = Column(Integer, ForeignKey("categoria_problema.id"), nullable=False)
    idCliente = Column(Integer, ForeignKey("cliente.id"), nullable=False, index=True)
    placaVehiculo = Column(String(20), ForeignKey("vehiculo.placa"), nullable=False, index=True)
    idEstado = Column(Integer, ForeignKey("estado.id"), nullable=False, index=True, server_default="1") # 1 = INICIADA

    # Concurrencia/Mutex
    locked_by = Column(String(10), ForeignKey("taller.cod"), nullable=True)
    locked_at = Column(DateTime, nullable=True)
    
    # Audio raw (Whisper source)
    audio_url = Column(String(500), nullable=True)

    # Relaciones
    taller = relationship("Taller", back_populates="emergencias", foreign_keys=[idTaller])
    prioridad = relationship("Prioridad")
    categoria = relationship("CategoriaProblema")
    cliente = relationship("Cliente", back_populates="emergencias")
    vehiculo = relationship("Vehiculo", back_populates="emergencias")
    pago = relationship("Pago", back_populates="emergencia", uselist=False, cascade="all, delete-orphan")
    estado = relationship("Estado")
    evidencias = relationship("Evidencia", back_populates="emergencia", cascade="all, delete-orphan")
    historial = relationship("HistorialEstado", back_populates="emergencia", cascade="all, delete-orphan")
    resumen_ia = relationship("ResumenIA", back_populates="emergencia", uselist=False, cascade="all, delete-orphan")
    
    # Técnicos asignados (Muchos a Muchos)
    tecnicos_asignados = relationship("Tecnico", secondary="asignacion_tecnico_emergencia", back_populates="emergencias_asignadas")

    locker = relationship("Taller", foreign_keys=[locked_by])
    mensajes_chat = relationship("MensajeChat", back_populates="emergencia", cascade="all, delete-orphan")
