from pydantic import BaseModel
from typing import List, Optional

class KpiResumen(BaseModel):
    total_activas: int
    total_atendidas: int
    tiempo_promedio_asignacion: float
    tiempo_promedio_llegada: float
    tiempo_respuesta_minutos: float
    tasa_asignacion: float
    calificacion_promedio: float
    tasa_cumplimiento_sla: float

class TipoIncidente(BaseModel):
    tipo: str
    cantidad: int

class ZonaIncidente(BaseModel):
    zona: str
    cantidad: int

class RankingSucursal(BaseModel):
    sucursal: str
    eficiencia_promedio_min: float
    atendidas: int

class AnaliticaAvanzada(BaseModel):
    incidentes_por_tipo: List[TipoIncidente]
    zonas_incidentes: List[ZonaIncidente]
    ranking_sucursales: List[RankingSucursal]

class GraficaKpi(BaseModel):
    fecha: str
    atendidas: int
    activas: int

class KpiResponse(BaseModel):
    kpis: KpiResumen
    analitica: AnaliticaAvanzada
    grafica: List[GraficaKpi]
