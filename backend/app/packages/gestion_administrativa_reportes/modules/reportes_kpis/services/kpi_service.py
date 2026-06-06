from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta

from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.emergencia import Emergencia
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.estado import Estado
from app.packages.gestion_administrativa_reportes.modules.reportes_kpis.schemas.kpi_schema import (
    KpiResponse, KpiResumen, AnaliticaAvanzada, GraficaKpi, TipoIncidente, ZonaIncidente, RankingSucursal
)

from sqlalchemy.orm import selectinload

class KpiService:
    @staticmethod
    async def obtener_kpis(db: AsyncSession, id_taller: str, id_sucursal: int = None, rango: str = "mensual") -> KpiResponse:
        hoy = datetime.now()
        if rango == "diario":
            fecha_inicio = hoy - timedelta(days=1)
        elif rango == "semanal":
            fecha_inicio = hoy - timedelta(days=7)
        else: # mensual
            fecha_inicio = hoy - timedelta(days=30)
            
        # 1. Base Query para el Taller
        base_query = (
            select(Emergencia)
            .options(selectinload(Emergencia.tecnicos_asignados))
            .where(
                Emergencia.idTaller == id_taller,
                Emergencia.fecha >= fecha_inicio.date()
            )
        )
        if id_sucursal:
            base_query = base_query.where(Emergencia.idSucursal == id_sucursal)
            
        res_emergencias = await db.execute(base_query)
        emergencias = res_emergencias.scalars().all()
        
        # Obtener los IDs de estados de la tabla Estado
        res_estados = await db.execute(select(Estado))
        estados = {e.id: e.nombre for e in res_estados.scalars().all()}
        
        # Mapear estados a nombres
        activas = [e for e in emergencias if estados.get(e.idEstado) not in ["Finalizada", "Cancelada"]]
        atendidas = [e for e in emergencias if estados.get(e.idEstado) == "Finalizada"]
        
        total_activas = len(activas)
        total_atendidas = len(atendidas)
        
        tiempo_promedio_asignacion = 15.0 # min
        tiempo_promedio_llegada = 45.0 # min
        tiempo_respuesta_minutos = 60.0 # min
        
        tasa_asignacion = (len([e for e in emergencias if e.tecnicos_asignados]) / len(emergencias)) * 100 if emergencias else 0.0
        calificacion_promedio = 4.8 # Hardcoded for now
        tasa_cumplimiento_sla = 90.0 # Hardcoded for now
        
        kpi_resumen = KpiResumen(
            total_activas=total_activas,
            total_atendidas=total_atendidas,
            tiempo_promedio_asignacion=tiempo_promedio_asignacion,
            tiempo_promedio_llegada=tiempo_promedio_llegada,
            tiempo_respuesta_minutos=tiempo_respuesta_minutos,
            tasa_asignacion=tasa_asignacion,
            calificacion_promedio=calificacion_promedio,
            tasa_cumplimiento_sla=tasa_cumplimiento_sla
        )
        
        # Analitica Avanzada
        tipos_count = {}
        for e in emergencias:
            # Obtener nombre de la categoria o clasificacion de la emergencia
            # Simularemos esto por ahora basado en la descripcion
            tipo = "Mecánica"
            if e.descripcion and "llanta" in e.descripcion.lower(): tipo = "Neumáticos"
            elif e.descripcion and "bater" in e.descripcion.lower(): tipo = "Eléctrico"
            tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
            
        incidentes_por_tipo = [TipoIncidente(tipo=k, cantidad=v) for k, v in tipos_count.items()]
        
        # Simulación de Zonas
        zonas_incidentes = [
            ZonaIncidente(zona="Norte", cantidad=int(total_atendidas * 0.4)),
            ZonaIncidente(zona="Sur", cantidad=int(total_atendidas * 0.3)),
            ZonaIncidente(zona="Centro", cantidad=int(total_atendidas * 0.3))
        ]
        
        # Simulación de Sucursales
        ranking_sucursales = [
            RankingSucursal(sucursal="Principal", eficiencia_promedio_min=45.0, atendidas=total_atendidas)
        ]
        
        analitica = AnaliticaAvanzada(
            incidentes_por_tipo=incidentes_por_tipo,
            zonas_incidentes=zonas_incidentes,
            ranking_sucursales=ranking_sucursales
        )
        
        # Gráfica
        dias = (hoy.date() - fecha_inicio.date()).days
        grafica = []
        for i in range(dias + 1):
            dia_actual = fecha_inicio.date() + timedelta(days=i)
            
            emgs_dia = [e for e in emergencias if e.fecha == dia_actual]
            act_dia = len([e for e in emgs_dia if estados.get(e.idEstado) not in ["Finalizada", "Cancelada"]])
            atend_dia = len([e for e in emgs_dia if estados.get(e.idEstado) == "Finalizada"])
            
            grafica.append(GraficaKpi(
                fecha=dia_actual.strftime("%Y-%m-%d"),
                atendidas=atend_dia,
                activas=act_dia
            ))
            
        return KpiResponse(
            kpis=kpi_resumen,
            analitica=analitica,
            grafica=grafica
        )
