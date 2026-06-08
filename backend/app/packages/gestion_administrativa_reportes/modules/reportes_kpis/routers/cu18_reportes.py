from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract
from typing import Optional, List
from datetime import date, datetime, timedelta
from fpdf import FPDF

from app.db.session import get_db
from app.core.dependencies import require_role
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.emergencia import Emergencia
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.estado import Estado
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.packages.gestion_administrativa_reportes.modules.pagos.models.pago import Pago
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.tecnico import Tecnico
from app.packages.gestion_usuarios_seguridad.modules.tenants.schemas.sucursal_schema import UsuarioOut
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.schemas.vehiculo import VehiculoOut
from app.packages.gestion_administrativa_reportes.modules.reportes_kpis.services.historial_vehicular_service import HistorialVehicularService
from app.packages.gestion_administrativa_reportes.modules.reportes_kpis.schemas.kpi_schema import KpiResponse
from app.packages.gestion_administrativa_reportes.modules.reportes_kpis.services.kpi_service import KpiService

router = APIRouter(prefix="/reportes", tags=["Comercio — Reportes Taller"])

@router.get("/stats")
async def obtener_estadisticas_taller(
    mes: int = Query(default=datetime.now().month, ge=1, le=12),
    anio: int = Query(default=datetime.now().year),
    current=Depends(require_role("admin", "tecnico", "gerente", "supervisor", "admin_sucursal")),
    db: AsyncSession = Depends(get_db),
):
    taller_cod = current.get("taller")
    if not taller_cod:
        raise HTTPException(status_code=403, detail="No se encontró código de taller en la sesión.")

    # 1. Filtro base por taller, mes y año
    # Unimos con Pago para obtener los montos
    stmt = (
        select(
            func.count(Emergencia.id).label("total_servicios"),
            func.sum(Pago.monto).label("ingreso_bruto"),
            func.sum(Pago.monto_comision).label("comisiones_pagadas"),
            (func.sum(Pago.monto) - func.sum(Pago.monto_comision)).label("ingreso_neto")
        )
        .join(Pago, Emergencia.id == Pago.emergencia_id)
        .where(Emergencia.idTaller == taller_cod)
        .where(extract('month', Pago.fecha_pago) == mes)
        .where(extract('year', Pago.fecha_pago) == anio)
        .where(Pago.estado == "COMPLETADO")
    )
    
    res = await db.execute(stmt)
    stats = res.first()

    # 2. Desglose diario para la gráfica
    stmt_diario = (
        select(
            Pago.fecha_pago,
            func.sum(Pago.monto).label("monto_dia")
        )
        .join(Emergencia, Emergencia.id == Pago.emergencia_id)
        .where(Emergencia.idTaller == taller_cod)
        .where(extract('month', Pago.fecha_pago) == mes)
        .where(extract('year', Pago.fecha_pago) == anio)
        .where(Pago.estado == "COMPLETADO")
        .group_by(Pago.fecha_pago)
        .order_by(Pago.fecha_pago)
    )
    
    res_diario = await db.execute(stmt_diario)
    breakdown = [{"fecha": str(r.fecha_pago), "monto": float(r.monto_dia)} for r in res_diario.all()]

    return {
        "resumen": {
            "total_servicios": stats.total_servicios or 0,
            "ingreso_bruto": float(stats.ingreso_bruto or 0),
            "comisiones_pagadas": float(stats.comisiones_pagadas or 0),
            "ingreso_neto": float(stats.ingreso_neto or 0),
            "mes": mes,
            "anio": anio
        },
        "grafica": breakdown
    }

@router.get("/pdf")
async def generar_reporte_pdf(
    mes: int = Query(default=datetime.now().month),
    anio: int = Query(default=datetime.now().year),
    current=Depends(require_role("tecnico", "admin", "admin_sucursal")),
    db: AsyncSession = Depends(get_db),
):

    data = await obtener_estadisticas_taller(mes, anio, current, db)
    resumen = data["resumen"]
    taller_cod = current.get("taller")

    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 15, "REPORTE MENSUAL DE RENDIMIENTO", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Taller: {taller_cod}", ln=True, align="C")
    pdf.cell(0, 6, f"Periodo: {mes}/{anio}", ln=True, align="C")
    pdf.ln(10)

    # Cards
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(90, 10, "Concepto", 1, 0, "C", True)
    pdf.cell(90, 10, "Valor", 1, 1, "C", True)
    
    pdf.set_font("Helvetica", "", 11)
    items = [
        ("Servicios Realizados", f"{resumen['total_servicios']}"),
        ("Ingreso Bruto Total", f"${resumen['ingreso_bruto']:.2f}"),
        ("Comisiones Plataforma (10%)", f"${resumen['comisiones_pagadas']:.2f}"),
        ("Ingreso Neto (Para el Taller)", f"${resumen['ingreso_neto']:.2f}"),
    ]
    
    for label, val in items:
        pdf.cell(90, 10, label, 1)
        pdf.cell(90, 10, val, 1, 1, "R")

    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(0, 6, "Este reporte resume la actividad financiera del taller durante el mes seleccionado. Las comisiones son calculadas automáticamente sobre el ingreso bruto de cada servicio finalizado.")

    pdf_bytes = pdf.output()
    
    return Response(
        content=bytes(pdf_bytes), 
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=reporte_{taller_cod}_{mes}_{anio}.pdf"}
    )

@router.get("/kpis", response_model=KpiResponse)
async def obtener_kpis_dashboard(
    rango: str = Query(default="mensual", pattern="^(diario|semanal|mensual)$"),
    current_user: UsuarioOut = Depends(require_role("admin", "gerente", "supervisor", "tecnico", "admin_sucursal")),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene los KPIs clave (Ingresos, Trabajos Completados, Tasa de Conversión, Tiempos Promedio)
    para el taller del usuario autenticado, filtrados por rango de fecha.
    """
    return await KpiService.obtener_kpis(
        db, 
        current_user.get("taller"), 
        id_sucursal=current_user.get("sucursal"),
        rango=rango
    )


@router.get("/vehiculos-atendidos", response_model=List[VehiculoOut])
async def obtener_vehiculos_atendidos(
    current_user: UsuarioOut = Depends(require_role("admin", "gerente", "supervisor", "tecnico", "admin_sucursal")),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista los vehículos que han sido atendidos en este taller.
    """
    return await HistorialVehicularService.listar_vehiculos_atendidos(db, current_user.get("taller"))


@router.get("/vehiculos-atendidos/{placa}/historial")
async def obtener_historial_vehiculo(
    placa: str,
    current_user: UsuarioOut = Depends(require_role("admin", "gerente", "supervisor", "tecnico", "admin_sucursal")),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene la línea de tiempo completa de un vehículo en el taller.
    """
    return await HistorialVehicularService.obtener_historial_completo(db, current_user.get("taller"), placa)

from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.historial_estado import HistorialEstado
from sqlalchemy.orm import selectinload

@router.get("/kpis-legacy")
async def obtener_kpis_dashboard(
    rango: str = Query(default="mensual", description="diario, semanal, mensual"),
    current=Depends(require_role("tecnico", "admin", "admin_sucursal")),
    db: AsyncSession = Depends(get_db),
):
    taller_cod = current.get("taller")
    if not taller_cod:
        raise HTTPException(status_code=403, detail="No se encontró código de taller en la sesión.")

    taller = await Taller.get(db, taller_cod)
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado.")

    # Fechas
    hoy = date.today()
    if rango == "diario":
        fecha_inicio = hoy
    elif rango == "semanal":
        fecha_inicio = hoy - timedelta(days=7)
    else: # mensual
        fecha_inicio = hoy.replace(day=1)

    # Cargar emergencias con sus relaciones completas para cálculos avanzados en Python
    stmt = (
        select(Emergencia)
        .options(
            selectinload(Emergencia.estado),
            selectinload(Emergencia.categoria),
            selectinload(Emergencia.historial).selectinload(HistorialEstado.estado),
            selectinload(Emergencia.tecnicos_asignados).selectinload(Tecnico.sucursal)
        )
        .where(Emergencia.idTaller == taller_cod)
        .where(Emergencia.fecha >= fecha_inicio)
        .where(Emergencia.fecha <= hoy)
    )
    result = await db.execute(stmt)
    emergencias = result.scalars().all()

    # Contadores básicos
    activas = 0
    atendidas = 0
    canceladas = 0

    # Categorias y Zonas
    incidentes_por_tipo = {}
    incidentes_por_zona = {}

    # Tiempos
    tiempos_asignacion = []
    tiempos_llegada = []
    tiempos_resolucion_total = []

    # Ranking Sucursales: dict[nombre_sucursal, list_tiempos_resolucion]
    sucursales_eficiencia = {}

    SLA_MINUTOS = 60 # Esperado completar todo en 1 hora
    cumplimiento_sla_count = 0

    grafica_dict = {}

    for em in emergencias:
        estado_actual = em.estado.nombre
        fecha_str = str(em.fecha)

        if fecha_str not in grafica_dict:
            grafica_dict[fecha_str] = {"activas": 0, "atendidas": 0, "canceladas": 0}

        if estado_actual in ["ASIGNADO", "EN_RUTEO", "EN_PROGRESO", "ANALIZANDO"]:
            activas += 1
            grafica_dict[fecha_str]["activas"] += 1
        elif estado_actual in ["COMPLETADO", "FINALIZADO"]:
            atendidas += 1
            grafica_dict[fecha_str]["atendidas"] += 1
        elif estado_actual in ["CANCELADA", "RECHAZADA", "BLOQUEADO"]:
            canceladas += 1
            grafica_dict[fecha_str]["canceladas"] += 1

        # Categoria
        cat_name = em.categoria.descripcion if em.categoria else "Otra"
        incidentes_por_tipo[cat_name] = incidentes_por_tipo.get(cat_name, 0) + 1

        # Zona (usando un split simple de la direccion para extraer sector/zona)
        zona = em.direccion.split(',')[0].strip() if em.direccion else "Desconocida"
        incidentes_por_zona[zona] = incidentes_por_zona.get(zona, 0) + 1

        # Analizar Historial de Tiempos
        historial = sorted(em.historial, key=lambda h: h.fecha_cambio)
        t_inicio = None
        t_asignado = None
        t_progreso = None
        t_fin = None

        for h in historial:
            enombre = h.estado.nombre
            if enombre in ["INICIADA", "PENDIENTE"] and not t_inicio:
                t_inicio = h.fecha_cambio
            elif enombre in ["ASIGNADO", "EN_RUTEO"] and not t_asignado:
                t_asignado = h.fecha_cambio
            elif enombre == "EN_PROGRESO" and not t_progreso:
                t_progreso = h.fecha_cambio
            elif enombre in ["COMPLETADO", "FINALIZADO"] and not t_fin:
                t_fin = h.fecha_cambio

        if t_inicio and t_asignado:
            diff = (t_asignado - t_inicio).total_seconds() / 60.0
            if diff > 0: tiempos_asignacion.append(diff)
        
        if t_asignado and t_progreso:
            diff = (t_progreso - t_asignado).total_seconds() / 60.0
            if diff > 0: tiempos_llegada.append(diff)
            
        if t_inicio and t_fin:
            diff_total = (t_fin - t_inicio).total_seconds() / 60.0
            if diff_total > 0:
                tiempos_resolucion_total.append(diff_total)
                if diff_total <= SLA_MINUTOS:
                    cumplimiento_sla_count += 1
                
                # Asignar a sucursal
                suc_name = "Principal"
                if em.tecnicos_asignados and em.tecnicos_asignados[0].sucursal:
                    suc_name = em.tecnicos_asignados[0].sucursal.nombre
                
                if suc_name not in sucursales_eficiencia:
                    sucursales_eficiencia[suc_name] = []
                sucursales_eficiencia[suc_name].append(diff_total)


    # Promedios
    avg_asignacion = sum(tiempos_asignacion)/len(tiempos_asignacion) if tiempos_asignacion else 0
    avg_llegada = sum(tiempos_llegada)/len(tiempos_llegada) if tiempos_llegada else 0
    avg_resolucion = sum(tiempos_resolucion_total)/len(tiempos_resolucion_total) if tiempos_resolucion_total else 0
    
    total_evaluadas = atendidas + canceladas
    tasa_asignacion = (atendidas / total_evaluadas * 100) if total_evaluadas > 0 else 0.0
    tasa_sla = (cumplimiento_sla_count / atendidas * 100) if atendidas > 0 else 0.0

    ranking_list = []
    for suc, list_tiempos in sucursales_eficiencia.items():
        ranking_list.append({
            "sucursal": suc,
            "eficiencia_promedio_min": sum(list_tiempos)/len(list_tiempos) if list_tiempos else 0,
            "atendidas": len(list_tiempos)
        })
    ranking_list.sort(key=lambda x: x["eficiencia_promedio_min"]) # Menor tiempo es mas eficiente

    breakdown = [{"fecha": k, **v} for k, v in sorted(grafica_dict.items(), key=lambda x: x[0])]

    return {
        "kpis": {
            "total_activas": activas,
            "total_atendidas": atendidas,
            "tiempo_promedio_asignacion": round(avg_asignacion, 1),
            "tiempo_promedio_llegada": round(avg_llegada, 1),
            "tiempo_respuesta_minutos": round(avg_resolucion, 1), # Tiempo total de resolucion
            "tasa_asignacion": round(tasa_asignacion, 1),
            "calificacion_promedio": taller.calificacion_promedio,
            "tasa_cumplimiento_sla": round(tasa_sla, 1)
        },
        "analitica": {
            "incidentes_por_tipo": [{"tipo": k, "cantidad": v} for k, v in incidentes_por_tipo.items()],
            "zonas_incidentes": sorted([{"zona": k, "cantidad": v} for k, v in incidentes_por_zona.items()], key=lambda x: x["cantidad"], reverse=True)[:5],
            "ranking_sucursales": ranking_list[:5]
        },
        "grafica": breakdown
    }
