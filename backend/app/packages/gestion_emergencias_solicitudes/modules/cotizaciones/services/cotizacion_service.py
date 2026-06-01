from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone

from app.packages.gestion_emergencias_solicitudes.modules.cotizaciones.repositories.cotizacion_repo import CotizacionRepository
from app.packages.gestion_emergencias_solicitudes.modules.cotizaciones.schemas.cotizacion import CotizacionCreate, CotizacionUpdate

from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.emergencia import Emergencia
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.estado import Estado
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.core.socket_manager import manager

class CotizacionService:
    def __init__(self, db: Session):
        self.repo = CotizacionRepository(db)
        self.db = db

    def create_cotizacion(self, id_emergencia: int, id_taller: str, data: CotizacionCreate):
        # Verificar si ya existe una de este taller para esta emergencia
        existente = self.repo.get_by_emergencia_and_taller(id_emergencia, id_taller)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El taller ya ha emitido una cotización para esta emergencia"
            )
            
        cotizacion = self.repo.create(
            idEmergencia=id_emergencia,
            idTaller=id_taller,
            descripcion_servicio=data.descripcion_servicio,
            costo_mano_obra=data.costo_mano_obra,
            costo_repuestos=data.costo_repuestos,
            tiempo_estimado_horas=data.tiempo_estimado_horas,
            condiciones=data.condiciones,
            estado="PENDIENTE"
        )
        return cotizacion

    def get_cotizaciones_by_emergencia(self, id_emergencia: int):
        return self.repo.get_by_emergencia(id_emergencia)

    async def update_estado_async(self, id_cotizacion: int, data: CotizacionUpdate):
        cotizacion = self.repo.get_by_id(id_cotizacion)
        if not cotizacion:
            raise HTTPException(status_code=404, detail="Cotización no encontrada")
            
        if data.estado == "ACEPTADA":
            # 1. Verificar Expiración (10 min)
            ahora = datetime.now()
            # Asumimos que fecha_creacion es naive local, o adaptamos según timezone
            diferencia = ahora - cotizacion.fecha_creacion
            if diferencia > timedelta(minutes=10):
                raise HTTPException(status_code=400, detail="La cotización ha expirado (más de 10 minutos).")

            # 2. Verificar que el Taller siga ACTIVO
            taller = self.db.query(Taller).filter(Taller.cod == cotizacion.idTaller).first()
            if not taller or taller.estado != "ACTIVO":
                raise HTTPException(status_code=400, detail="El taller ya no está disponible.")

        # Actualizar estado de la cotización actual
        updates = {"estado": data.estado}
        if data.condiciones is not None:
            updates["condiciones"] = data.condiciones
            
        self.repo.update(cotizacion, **updates)

        if data.estado == "ACEPTADA":
            # 1. Asignar el taller a la emergencia
            emergencia = self.db.query(Emergencia).filter(Emergencia.id == cotizacion.idEmergencia).first()
            if emergencia:
                emergencia.idTaller = cotizacion.idTaller
                # Buscar estado ASIGNADO
                estado_asignado = self.db.query(Estado).filter(Estado.nombre == "ASIGNADO").first()
                if estado_asignado:
                    emergencia.idEstado = estado_asignado.id
                self.db.commit()

            # 2. Notificar al taller ganador
            await manager.send_personal_message(
                {"type": "cotizacion_aceptada", "emergencia_id": cotizacion.idEmergencia, "mensaje": "¡El cliente aceptó tu cotización!"}, 
                f"taller_{cotizacion.idTaller}"
            )

            # 3. Rechazar todas las demás cotizaciones para esta emergencia y notificar
            otras_cotizaciones = self.db.query(self.repo.model).filter(
                self.repo.model.idEmergencia == cotizacion.idEmergencia,
                self.repo.model.id != cotizacion.id
            ).all()

            for otra in otras_cotizaciones:
                self.repo.update(otra, estado="RECHAZADA")
                await manager.send_personal_message(
                    {"type": "cotizacion_rechazada", "emergencia_id": cotizacion.idEmergencia, "mensaje": "El cliente seleccionó otro taller."}, 
                    f"taller_{otra.idTaller}"
                )

        return cotizacion

