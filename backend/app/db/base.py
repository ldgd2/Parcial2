from app.db.session import Base

# ==============================================================================
# IMPORTACIÓN CENTRALIZADA DE MODELOS PARA ALEMBIC
# ==============================================================================
# Al importar todos los modelos aquí, Alembic (a través de Base.metadata)
# podrá detectar automáticamente los cambios en la estructura de la base de datos,
# sin importar en qué paquete o módulo se encuentren.

# Paquete 1: Gestion Usuarios y Seguridad
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.usuario import Usuario
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.vehiculo import Vehiculo
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.cliente import Cliente
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.tecnico import Tecnico
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.tecnico_especialidad import TecnicoEspecialidad
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.especialidad import Especialidad
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller

# Paquete 2: Gestion Emergencias y Solicitudes
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.emergencia import Emergencia
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.historial_estado import HistorialEstado
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.estado import Estado
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.prioridad import Prioridad
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.categoria_problema import CategoriaProblema
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.evidencia import Evidencia
from app.packages.gestion_emergencias_solicitudes.modules.auxilio_solicitudes.models.asignacion_tecnico_emergencia import AsignacionTecnicoEmergencia
from app.packages.gestion_emergencias_solicitudes.modules.auxilio_solicitudes.models.asignacion_especialidad import AsignacionEspecialidad
from app.packages.gestion_emergencias_solicitudes.modules.cotizaciones.models.cotizacion import Cotizacion

# Paquete 3: IA y Automatizacion
from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.models.resumen_ia import ResumenIA
from app.packages.inteligencia_artificial_automatizacion.modules.notificaciones.models.mensaje_chat import MensajeChat
from app.packages.inteligencia_artificial_automatizacion.modules.notificaciones.models.fcm_token import FCMToken

# Paquete 4: Administrativa y Reportes
from app.packages.gestion_administrativa_reportes.modules.pagos.models.pago import Pago
from app.packages.gestion_administrativa_reportes.modules.pagos.models.metodo_pago import MetodoPago
from app.packages.gestion_administrativa_reportes.modules.reportes_kpis.models.bitacora import Bitacora

# Exponer Base para alembic/env.py
__all__ = ["Base"]
