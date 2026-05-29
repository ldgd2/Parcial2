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
from app.packages.gestion_administrativa_reportes.modules.pagos.models.pago import Pago

router = APIRouter(prefix="/reportes", tags=["Comercio — Reportes Taller"])

@router.get("/stats")
async def obtener_estadisticas_taller(
    mes: int = Query(default=datetime.now().month, ge=1, le=12),
    anio: int = Query(default=datetime.now().year),
    current=Depends(require_role("tecnico", "admin")),
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
    current=Depends(require_role("tecnico", "admin")),
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
