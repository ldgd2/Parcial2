from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone

from app.packages.gestion_emergencias_solicitudes.modules.cotizaciones.schemas.cotizacion import CotizacionCreate, CotizacionUpdate, CotizacionAjuste

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
            
        subtotal_productos = sum(item.precio * item.cantidad for item in data.lista_productos)
        subtotal_servicios = sum(item.precio for item in data.lista_servicios)
        total_general = subtotal_productos + subtotal_servicios

        if existente:
            if existente.estado == "ACEPTADA":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La cotización ya fue aceptada. No se puede emitir otra."
                )
            
            # Actualizamos la cotización existente y la ponemos en PENDIENTE
            cotizacion = await self.repo.update(db_obj=existente, obj_in={
                "descripcion_servicio": data.descripcion_servicio,
                "moneda": data.moneda,
                "lista_productos": [item.dict() for item in data.lista_productos],
                "lista_servicios": [item.dict() for item in data.lista_servicios],
                "subtotal_productos": subtotal_productos,
                "subtotal_servicios": subtotal_servicios,
                "total_general": total_general,
                "tiempo_estimado": data.tiempo_estimado,
                "condiciones": data.condiciones,
                "estado": "PENDIENTE"
            })
        else:
            cotizacion = await self.repo.create(obj_in={
                "idEmergencia": id_emergencia,
                "idTaller": id_taller,
                "descripcion_servicio": data.descripcion_servicio,
                "moneda": data.moneda,
                "lista_productos": [item.dict() for item in data.lista_productos],
                "lista_servicios": [item.dict() for item in data.lista_servicios],
                "subtotal_productos": subtotal_productos,
                "subtotal_servicios": subtotal_servicios,
                "total_general": total_general,
                "tiempo_estimado": data.tiempo_estimado,
                "condiciones": data.condiciones,
                "estado": "PENDIENTE"
            })
        
        from sqlalchemy import select
        from sqlalchemy.orm import joinedload
        result = await self.db.execute(
            select(self.repo.model)
            .options(joinedload(self.repo.model.taller))
            .where(self.repo.model.id == cotizacion.id)
            .execution_options(populate_existing=True)
        )
        cot_with_taller = result.scalar_one()

        # Notificar al cliente
        res_emergencia = await self.db.execute(select(Emergencia).where(Emergencia.id == id_emergencia))
        emergencia = res_emergencia.scalar_one_or_none()
        if emergencia:
            from app.packages.inteligencia_artificial_automatizacion.modules.notificaciones.services.notification_service import NotificationService
            taller_nombre = cot_with_taller.taller.nombre if (hasattr(cot_with_taller, 'taller') and cot_with_taller.taller) else "Un taller"
            await NotificationService.enviar_notificacion_usuario(
                self.db,
                emergencia.idCliente,
                "Nueva Cotización",
                f"¡{taller_nombre} te ha enviado una cotización!",
                {"type": "nueva_cotizacion", "emergencia_id": id_emergencia}
            )

        return cot_with_taller

    async def get_cotizaciones_by_emergencia(self, id_emergencia: int):
        return await self.repo.get_by_emergencia(id_emergencia)

    async def update_estado_async(self, id_cotizacion: int, data: CotizacionUpdate):
        from sqlalchemy import select
        from sqlalchemy.orm import joinedload
        result = await self.db.execute(
            select(self.repo.model)
            .options(joinedload(self.repo.model.taller))
            .where(self.repo.model.id == id_cotizacion)
        )
        cotizacion = result.scalar_one_or_none()
        if not cotizacion:
            raise HTTPException(status_code=404, detail="Cotización no encontrada")
            
        if data.estado == "ACEPTADA":
            # 1. (Eliminado) Expiración removida según solicitud del usuario

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
                # Mantener en estado INICIADA (1) para que el Taller luego asigne al mecánico
                await emergencia.update(self.db, obj_in={
                    "idTaller": cotizacion.idTaller,
                    "idEstado": 1
                })
                from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.historial_estado import HistorialEstado
                await HistorialEstado.create(self.db, obj_in={
                    "idEmergencia": emergencia.id,
                    "idEstado": 1
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

    async def ajustar_cotizacion_async(self, id_cotizacion: int, data: "CotizacionAjuste"):
        cotizacion = await self.repo.get(id_cotizacion)
        if not cotizacion:
            raise HTTPException(status_code=404, detail="Cotización no encontrada")

        subtotal_productos = sum(item.precio * item.cantidad for item in data.lista_productos)
        subtotal_servicios = sum(item.precio for item in data.lista_servicios)
        total_general = subtotal_productos + subtotal_servicios

        updates = {
            "lista_productos": [item.dict() for item in data.lista_productos],
            "lista_servicios": [item.dict() for item in data.lista_servicios],
            "subtotal_productos": subtotal_productos,
            "subtotal_servicios": subtotal_servicios,
            "total_general": total_general,
        }
        if data.descripcion_servicio is not None:
            updates["descripcion_servicio"] = data.descripcion_servicio

        cotizacion = await self.repo.update(db_obj=cotizacion, obj_in=updates)

        # Notify via WebSocket to the emergency room
        room_id = f"emergencia_{cotizacion.idEmergencia}"
        await manager.broadcast_to_room(room_id, {
            "type": "cotizacion_ajustada",
            "message": "El técnico ha ajustado la cotización en el sitio.",
            "total_general": total_general,
            "subtotal_productos": subtotal_productos,
            "subtotal_servicios": subtotal_servicios
        })

        return cotizacion

    async def cancelar_por_cliente(self, id_cotizacion: int):
        from sqlalchemy import select
        from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.emergencia import Emergencia
        
        cotizacion = await self.repo.get(id_cotizacion)
        if not cotizacion:
            raise HTTPException(status_code=404, detail="Cotizacin no encontrada")
        if cotizacion.estado != "ACEPTADA":
            raise HTTPException(status_code=400, detail="Solo se pueden cancelar cotizaciones aceptadas.")

        # Actualizamos cotizacin
        cotizacion = await self.repo.update(db_obj=cotizacion, obj_in={"estado": "CANCELADA"})

        # Obtenemos la emergencia para quitarle el taller asignado y sumar deuda
        result_emergencia = await self.db.execute(select(Emergencia).where(Emergencia.id == cotizacion.idEmergencia))
        emergencia = result_emergencia.scalar_one_or_none()
        
        if emergencia:
            await emergencia.update(self.db, obj_in={
                "idTaller": None,
                "deuda_acumulada": emergencia.deuda_acumulada + 5.0
            })
            
            # Notificar al taller
            await manager.send_personal_message(
                {
                    "type": "cotizacion_cancelada_cliente",
                    "emergencia_id": emergencia.id,
                    "mensaje": "El cliente cancel el servicio en curso. Se le ha cobrado una comisin a tu favor."
                },
                f"taller_{cotizacion.idTaller}"
            )

        return cotizacion
