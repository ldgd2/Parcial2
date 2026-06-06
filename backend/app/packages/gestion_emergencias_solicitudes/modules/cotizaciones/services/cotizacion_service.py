from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone

from app.packages.gestion_emergencias_solicitudes.modules.cotizaciones.schemas.cotizacion import CotizacionCreate, CotizacionUpdate

from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.emergencia import Emergencia
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.estado import Estado
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.core.socket_manager import manager

from app.packages.gestion_emergencias_solicitudes.modules.cotizaciones.repositories.cotizacion_repo import CotizacionRepository

class CotizacionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CotizacionRepository(db)

    async def create_cotizacion(self, id_emergencia: int, id_taller: str, data: CotizacionCreate):
        # Verificar si ya existe una de este taller para esta emergencia
        existente = await self.repo.get_by_emergencia_and_taller(id_emergencia, id_taller)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El taller ya ha emitido una cotización para esta emergencia"
            )
            
        cotizacion = await self.repo.create(
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

    async def get_cotizaciones_by_emergencia(self, id_emergencia: int):
        return await self.repo.get_by_emergencia(id_emergencia)

    async def update_estado_async(self, id_cotizacion: int, data: CotizacionUpdate):
        cotizacion = await self.repo.get(id_cotizacion)
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
            from sqlalchemy import select
            result_taller = await self.db.execute(select(Taller).where(Taller.cod == cotizacion.idTaller))
            taller = result_taller.scalar_one_or_none()
            if not taller or taller.estado != "ACTIVO":
                raise HTTPException(status_code=400, detail="El taller ya no está disponible.")

        # Actualizar estado de la cotización actual
        updates = {"estado": data.estado}
        if data.condiciones is not None:
            updates["condiciones"] = data.condiciones
            
        await self.repo.update(db_obj=cotizacion, obj_in=updates)

        if data.estado == "ACEPTADA":
            # 1. Asignar el taller a la emergencia
            result_emergencia = await self.db.execute(select(Emergencia).where(Emergencia.id == cotizacion.idEmergencia))
            emergencia = result_emergencia.scalar_one_or_none()
            if emergencia:
                # Buscar estado ASIGNADO
                estado_asignado = await Estado.get_by_nombre(self.db, "ASIGNADO")
                nuevo_id_estado = estado_asignado.id if estado_asignado else 2
                
                await emergencia.update(self.db, obj_in={
                    "idTaller": cotizacion.idTaller,
                    "idEstado": nuevo_id_estado
                })
                from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.historial_estado import HistorialEstado
                await HistorialEstado.create(self.db, obj_in={
                    "idEmergencia": emergencia.id,
                    "idEstado": nuevo_id_estado
                })
                await self.db.commit()

            # 2. Notificar al taller ganador
            await manager.send_personal_message(
                {"type": "cotizacion_aceptada", "emergencia_id": cotizacion.idEmergencia, "mensaje": "¡El cliente aceptó tu cotización!"}, 
                f"taller_{cotizacion.idTaller}"
            )

            # 3. Rechazar todas las demás cotizaciones para esta emergencia y notificar
            result_otras = await self.db.execute(
                select(self.repo.model).where(
                    self.repo.model.idEmergencia == cotizacion.idEmergencia,
                    self.repo.model.id != cotizacion.id
                )
            )
            otras_cotizaciones = result_otras.scalars().all()

            for otra in otras_cotizaciones:
                await self.repo.update(db_obj=otra, obj_in={"estado": "RECHAZADA"})
                await manager.send_personal_message(
                    {"type": "cotizacion_rechazada", "emergencia_id": cotizacion.idEmergencia, "mensaje": "El cliente seleccionó otro taller."}, 
                    f"taller_{otra.idTaller}"
                )

        return cotizacion

