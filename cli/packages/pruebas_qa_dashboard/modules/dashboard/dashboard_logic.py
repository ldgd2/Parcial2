import os
import sys
from sqlalchemy import select, func

sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.db.session import AsyncSessionLocal
from app.db.base import Base # Esto precarga todos los modelos y resuelve los problemas de Mapper de SQLAlchemy
from app.packages.gestion_administrativa_reportes.modules.pagos.models.pago import Pago
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.emergencia import Emergencia
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.estado import Estado

async def get_stats_async():
    async with AsyncSessionLocal() as db:
        # 1. Obtener ID de estado FINALIZADA
        est_res = await db.execute(select(Estado.id).where(Estado.nombre == "FINALIZADA"))
        finalizada_id = est_res.scalar() or 8

        # 2. Total Pagos Completados
        total_pagos_res = await db.execute(
            select(func.sum(Pago.monto)).where(Pago.estado == "COMPLETADO")
        )
        total_pagos = total_pagos_res.scalar() or 0.0
        
        # 3. Total Comisiones (Plataforma)
        total_comision_res = await db.execute(
            select(func.sum(Pago.monto_comision)).where(Pago.estado == "COMPLETADO")
        )
        total_comision = total_comision_res.scalar() or 0.0
        
        # 4. Ganancia Neta Talleres
        ganancia_neta = float(total_pagos) - float(total_comision)
        
        # 5. Conteo de Emergencias Finalizadas
        finalizadas_res = await db.execute(
            select(func.count(Emergencia.id)).where(Emergencia.idEstado == finalizada_id)
        )
        total_finalizadas = finalizadas_res.scalar() or 0
        
        # 6. Desglose por Taller
        taller_stats_stmt = (
            select(
                Taller.nombre,
                func.sum(Pago.monto),
                func.sum(Pago.monto_comision),
                func.count(Emergencia.id)
            )
            .join(Emergencia, Emergencia.idTaller == Taller.cod)
            .join(Pago, Pago.emergencia_id == Emergencia.id)
            .where(Pago.estado == "COMPLETADO")
            .group_by(Taller.nombre)
        )
        taller_stats_res = await db.execute(taller_stats_stmt)
        taller_stats = taller_stats_res.all()
        
        return {
            "total_pagos": total_pagos,
            "total_comision": total_comision,
            "ganancia_neta": ganancia_neta,
            "total_finalizadas": total_finalizadas,
            "taller_stats": taller_stats
        }
