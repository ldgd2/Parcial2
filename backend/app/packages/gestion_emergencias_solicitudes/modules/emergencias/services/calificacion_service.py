from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.calificacion import Calificacion
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.emergencia import Emergencia
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.tecnico import Tecnico
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.usuario import Usuario
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.schemas.calificacion_schema import CalificacionCreate, ModerarCalificacion
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.schemas.emergencia import EmergenciaOut

class CalificacionService:

    @staticmethod
    async def crear_calificacion(db: AsyncSession, id_emergencia: int, id_cliente: int, data: CalificacionCreate):
        # 1. Verificar existencia y estado de la emergencia
        result = await db.execute(
            select(Emergencia).where(Emergencia.id == id_emergencia)
        )
        emergencia = result.scalar_one_or_none()

        if not emergencia:
            raise HTTPException(status_code=404, detail="Emergencia no encontrada.")

        if emergencia.idCliente != id_cliente:
            raise HTTPException(status_code=403, detail="No puedes calificar una emergencia de otro cliente.")

        # Verificar que el estado sea COMPLETADO o FINALIZADO o ATENDIDO. 
        # (El estado "FINALIZADO"/"COMPLETADO" en base de datos es 6 - Atendido/Finalizado).
        if emergencia.idEstado != 6:
            raise HTTPException(status_code=400, detail="Solo se pueden calificar emergencias finalizadas.")

        # 2. Verificar que no haya sido calificada previamente
        result_calif = await db.execute(
            select(Calificacion).where(Calificacion.idEmergencia == id_emergencia)
        )
        calificacion_existente = result_calif.scalar_one_or_none()

        if calificacion_existente:
            raise HTTPException(status_code=400, detail="Esta emergencia ya ha sido calificada.")

        # Obtener el técnico asignado. Como es 1 a muchos, tomamos el primero asignado de la tabla intermedia o esperamos que el front mande a quién?
        # En la BD tenemos 'tecnicos_asignados'. Vamos a tomar el primero (es lo más común para este requerimiento).
        result_techs = await db.execute(
            select(Tecnico).join(Tecnico.emergencias_asignadas).where(Emergencia.id == id_emergencia)
        )
        tecnico = result_techs.scalars().first()
        id_tecnico = tecnico.id if tecnico else None

        if not id_tecnico:
            # Si por alguna razón no hay técnico asignado pero está finalizada
            raise HTTPException(status_code=400, detail="No hay un técnico asignado a esta emergencia para calificar.")

        # 3. Crear Calificación
        nueva_calificacion = Calificacion(
            idEmergencia=id_emergencia,
            idCliente=id_cliente,
            idTaller=emergencia.idTaller,
            idTecnico=id_tecnico,
            puntuacion_taller=data.puntuacion_taller,
            puntuacion_tecnico=data.puntuacion_tecnico,
            comentario=data.comentario,
            estado="PUBLICADA"
        )
        db.add(nueva_calificacion)
        await db.commit()
        await db.refresh(nueva_calificacion)

        # 4. Actualizar promedios
        await CalificacionService._actualizar_promedios(db, emergencia.idTaller, id_tecnico)

        return nueva_calificacion

    @staticmethod
    async def editar_calificacion(db: AsyncSession, id_calificacion: int, id_cliente: int, data: CalificacionCreate):
        result = await db.execute(select(Calificacion).where(Calificacion.id == id_calificacion))
        calificacion = result.scalar_one_or_none()

        if not calificacion:
            raise HTTPException(status_code=404, detail="Calificación no encontrada.")
        
        if calificacion.idCliente != id_cliente:
            raise HTTPException(status_code=403, detail="No tienes permiso para editar esta calificación.")

        calificacion.puntuacion_taller = data.puntuacion_taller
        calificacion.puntuacion_tecnico = data.puntuacion_tecnico
        calificacion.comentario = data.comentario
        
        await db.commit()
        await db.refresh(calificacion)

        # 4. Actualizar promedios
        await CalificacionService._actualizar_promedios(db, calificacion.idTaller, calificacion.idTecnico)

        return calificacion

    @staticmethod
    async def obtener_calificacion_cliente(db: AsyncSession, id_emergencia: int, id_cliente: int):
        result = await db.execute(
            select(Calificacion).where(
                Calificacion.idEmergencia == id_emergencia,
                Calificacion.idCliente == id_cliente
            )
        )
        calificacion = result.scalar_one_or_none()
        if not calificacion:
            raise HTTPException(status_code=404, detail="No has calificado esta emergencia.")
        return calificacion

    @staticmethod
    async def listar_pendientes_cliente(db: AsyncSession, id_cliente: int):
        # Emergencias FINALIZADAS (idEstado=6) del cliente que NO están en la tabla Calificacion
        query = select(Emergencia).outerjoin(
            Calificacion, Emergencia.id == Calificacion.idEmergencia
        ).where(
            Emergencia.idCliente == id_cliente,
            Emergencia.idEstado == 6,
            Calificacion.id == None
        )
        result = await db.execute(query)
        pendientes = result.scalars().all()
        return pendientes

    @staticmethod
    async def listar_calificaciones_taller(db: AsyncSession, id_taller: str, solo_publicas: bool = False):
        # Para el moderador/administrador del taller o publico
        query = select(Calificacion, Usuario, Tecnico).join(
            Usuario, Calificacion.idCliente == Usuario.id
        ).outerjoin(
            Tecnico, Calificacion.idTecnico == Tecnico.id
        ).where(
            Calificacion.idTaller == id_taller
        )
        
        if solo_publicas:
            query = query.where(Calificacion.estado == "PUBLICADA")

        query = query.order_by(Calificacion.fecha.desc())

        result = await db.execute(query)
        filas = result.all()

        salida = []
        for calif, usr, tec in filas:
            dict_calif = {
                "id": calif.id,
                "idEmergencia": calif.idEmergencia,
                "idCliente": calif.idCliente,
                "idTaller": calif.idTaller,
                "idTecnico": calif.idTecnico,
                "puntuacion_taller": calif.puntuacion_taller,
                "puntuacion_tecnico": calif.puntuacion_tecnico,
                "comentario": calif.comentario,
                "estado": calif.estado,
                "fecha": calif.fecha,
                "cliente_nombre": f"{usr.nombre} {usr.apellido}" if usr else "Cliente Anónimo",
                "tecnico_nombre": tec.nombre if tec else "Desconocido"
            }
            salida.append(dict_calif)

        return salida

    @staticmethod
    async def moderar_calificacion(db: AsyncSession, id_calificacion: int, data: ModerarCalificacion, id_taller: str):
        result = await db.execute(select(Calificacion).where(Calificacion.id == id_calificacion))
        calif = result.scalar_one_or_none()

        if not calif:
            raise HTTPException(status_code=404, detail="Calificación no encontrada.")
        
        if calif.idTaller != id_taller:
            raise HTTPException(status_code=403, detail="No autorizado para moderar esta calificación.")

        calif.estado = data.estado
        await db.commit()
        await db.refresh(calif)

        # Si se oculta o se publica de nuevo, recalcular promedios
        await CalificacionService._actualizar_promedios(db, calif.idTaller, calif.idTecnico)

        return calif

    @staticmethod
    async def _actualizar_promedios(db: AsyncSession, id_taller: str, id_tecnico: int):
        # Taller
        res_taller = await db.execute(
            select(func.avg(Calificacion.puntuacion_taller)).where(
                Calificacion.idTaller == id_taller,
                Calificacion.estado == "PUBLICADA"
            )
        )
        promedio_taller = res_taller.scalar() or 5.0
        
        await db.execute(
            select(Taller).where(Taller.cod == id_taller)
        )
        taller = (await db.execute(select(Taller).where(Taller.cod == id_taller))).scalar_one_or_none()
        if taller:
            taller.calificacion_promedio = round(promedio_taller, 1)

        # Técnico
        res_tecnico = await db.execute(
            select(func.avg(Calificacion.puntuacion_tecnico)).where(
                Calificacion.idTecnico == id_tecnico,
                Calificacion.estado == "PUBLICADA"
            )
        )
        promedio_tecnico = res_tecnico.scalar() or 5.0

        tecnico = (await db.execute(select(Tecnico).where(Tecnico.id == id_tecnico))).scalar_one_or_none()
        if tecnico:
            tecnico.calificacion_promedio = round(promedio_tecnico, 1)

        await db.commit()
