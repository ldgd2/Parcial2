from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from fastapi import HTTPException
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.emergencia import Emergencia
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.calificacion import Calificacion
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.vehiculo import Vehiculo
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.estado import Estado

class HistorialVehicularService:

    @staticmethod
    async def listar_vehiculos_atendidos(db: AsyncSession, id_taller: str):
        # Vehículos que han tenido al menos una emergencia en este taller
        query = select(Vehiculo).join(
            Emergencia, Vehiculo.placa == Emergencia.placaVehiculo
        ).where(
            Emergencia.idTaller == id_taller
        ).distinct()

        result = await db.execute(query)
        vehiculos = result.scalars().all()
        return vehiculos

    @staticmethod
    async def obtener_historial_completo(db: AsyncSession, id_taller: str, placa: str):
        # Validar si el vehículo ha sido atendido en este taller para proteger privacidad
        query_val = select(Emergencia).where(
            Emergencia.placaVehiculo == placa,
            Emergencia.idTaller == id_taller
        ).limit(1)
        res_val = await db.execute(query_val)
        if not res_val.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Este vehículo no tiene historial en tu taller.")

        # Obtener todas las emergencias de este vehículo, junto con calificacion y estado
        query = select(Emergencia, Calificacion, Estado).options(
            selectinload(Emergencia.pago)
        ).outerjoin(
            Calificacion, Emergencia.id == Calificacion.idEmergencia
        ).join(
            Estado, Emergencia.idEstado == Estado.id
        ).where(
            Emergencia.placaVehiculo == placa,
            Emergencia.idTaller == id_taller
        ).order_by(Emergencia.fecha.desc(), Emergencia.hora.desc())

        result = await db.execute(query)
        filas = result.all()

        historial = []
        for emg, calif, estado in filas:
            historial.append({
                "id_emergencia": emg.id,
                "fecha": emg.fecha,
                "estado_final": estado.nombre,
                "tipo_emergencia": getattr(emg, 'tipo_emergencia', 'Mecánica'),
                "diagnostico_inicial": emg.descripcion,
                "diagnostico_final": None,
                "servicios_realizados": None,
                "monto_total": emg.pago.monto if emg.pago else None,
                "calificacion_taller": calif.puntuacion_taller if calif else None,
                "calificacion_tecnico": calif.puntuacion_tecnico if calif else None
            })

        return historial
