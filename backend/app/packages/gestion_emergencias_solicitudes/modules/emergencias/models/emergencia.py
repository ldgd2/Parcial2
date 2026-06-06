from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, Column, Integer, String, Text, Date, Time, ForeignKey, func, Float, DateTime, Boolean, desc
from sqlalchemy.orm import relationship
from app.db.generic_model import GenericModel

# Importar modelos relacionados para que se registren en SQLAlchemy
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.sucursal import Sucursal
class Emergencia(GenericModel):
    __tablename__ = "emergencia"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(500), nullable=False)
    texto_adicional = Column("textoAdicional", Text, nullable=True)
    direccion = Column(String(500), nullable=False)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    es_valida = Column(Boolean, default=True, server_default="true")
    fecha = Column(Date, nullable=False, server_default=func.current_date())
    hora = Column(Time, nullable=False)
    uuid_local = Column(String(36), unique=True, index=True, nullable=True)

    # Claves foráneas (idTaller es nullable ahora hasta que alguien la tome)
    idTaller = Column(String(10), ForeignKey("public.taller.cod"), nullable=True, index=True)
    idSucursal = Column(Integer, ForeignKey("public.sucursal.id"), nullable=True, index=True)
    idPrioridad = Column(Integer, ForeignKey("public.prioridad.id"), nullable=False)
    idCategoria = Column(Integer, ForeignKey("public.categoria_problema.id"), nullable=False)
    idCliente = Column(Integer, ForeignKey("public.cliente.id"), nullable=False, index=True)
    placaVehiculo = Column(String(20), ForeignKey("public.vehiculo.placa"), nullable=False, index=True)
    idEstado = Column(Integer, ForeignKey("public.estado.id"), nullable=False, index=True, server_default="1") # 1 = INICIADA

    # Concurrencia/Mutex
    locked_by = Column(String(10), ForeignKey("public.taller.cod"), nullable=True)
    locked_at = Column(DateTime, nullable=True)
    
    # Audio raw (Whisper source)
    audio_url = Column(String(500), nullable=True)

    # Relaciones
    taller = relationship("Taller", back_populates="emergencias", foreign_keys=[idTaller])
    sucursal = relationship("Sucursal", foreign_keys=[idSucursal])
    prioridad = relationship("Prioridad")
    categoria = relationship("CategoriaProblema")
    cliente = relationship("Cliente", back_populates="emergencias")
    vehiculo = relationship("Vehiculo", back_populates="emergencias")
    pago = relationship("Pago", back_populates="emergencia", uselist=False, cascade="all, delete-orphan")
    calificacion = relationship("Calificacion", back_populates="emergencia", uselist=False, cascade="all, delete-orphan")
    estado = relationship("Estado")
    evidencias = relationship("Evidencia", back_populates="emergencia", cascade="all, delete-orphan")
    historial = relationship("HistorialEstado", back_populates="emergencia", cascade="all, delete-orphan")
    resumen_ia = relationship("ResumenIA", back_populates="emergencia", uselist=False, cascade="all, delete-orphan")
    cotizaciones = relationship("Cotizacion", back_populates="emergencia", cascade="all, delete-orphan")
    
    # Técnicos asignados (Muchos a Muchos)
    tecnicos_asignados = relationship("Tecnico", secondary="public.asignacion_tecnico_emergencia", back_populates="emergencias_asignadas")

    locker = relationship("Taller", foreign_keys=[locked_by])
    mensajes_chat = relationship("MensajeChat", back_populates="emergencia", cascade="all, delete-orphan")

    @classmethod
    def _get_detalle_options(cls):
        from sqlalchemy.orm import joinedload
        return [
            joinedload(cls.cliente),
            joinedload(cls.vehiculo),
            joinedload(cls.taller),
            joinedload(cls.prioridad),
            joinedload(cls.categoria),
            joinedload(cls.estado),
            joinedload(cls.evidencias),
            joinedload(cls.tecnicos_asignados)
        ]

    @classmethod
    async def get_detalle_by_id(cls, db: AsyncSession, emergencia_id: int) -> Optional["Emergencia"]:
        stmt = (
            select(cls)
            .options(*cls._get_detalle_options())
            .where(cls.id == emergencia_id)
        )
        result = await db.execute(stmt)
        return result.unique().scalar_one_or_none()

    @classmethod
    async def get_by_cliente(cls, db: AsyncSession, cliente_id: int) -> list["Emergencia"]:
        stmt = (
            select(cls)
            .options(*cls._get_detalle_options())
            .where(cls.idCliente == cliente_id)
            .order_by(desc(cls.fecha), desc(cls.hora))
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def get_by_taller(cls, db: AsyncSession, taller_cod: str) -> list["Emergencia"]:
        stmt = (
            select(cls)
            .options(*cls._get_detalle_options())
            .where(cls.idTaller == taller_cod)
            .order_by(desc(cls.fecha), desc(cls.hora))
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

