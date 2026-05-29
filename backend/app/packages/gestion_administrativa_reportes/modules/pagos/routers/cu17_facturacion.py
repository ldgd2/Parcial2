from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from fpdf import FPDF

from app.db.session import get_db
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.emergencia import Emergencia

router = APIRouter(prefix="/facturacion", tags=["Comercio — Facturación"])

@router.get("/{emergencia_id}/pdf")
async def descargar_factura_pdf(
    emergencia_id: int,
    db: AsyncSession = Depends(get_db),
):
    # Obtener emergencia con relaciones
    stmt = (
        select(Emergencia)
        .options(
            selectinload(Emergencia.pago),
            selectinload(Emergencia.taller),
            selectinload(Emergencia.cliente)
        )
        .where(Emergencia.id == emergencia_id)
    )
    res = await db.execute(stmt)
    emergencia = res.unique().scalar_one_or_none()
    
    if not emergencia or not emergencia.pago:
        raise HTTPException(status_code=404, detail="Factura no encontrada para esta emergencia.")
    
    pago = emergencia.pago
    detalle = pago.detalle_factura or {}
    
    # Generar PDF con fpdf2
    pdf = FPDF()
    pdf.add_page()
    
    # Fuentes y estilos
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(0, 10, "FACTURA DE SERVICIO", ln=True, align="C")
    
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 6, f"Factura No. {pago.id:06d}", ln=True, align="C")
    pdf.cell(0, 6, f"Fecha: {pago.fecha_pago}", ln=True, align="C")
    pdf.ln(10)
    
    # Datos del Taller
    taller = emergencia.taller
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(0, 8, "DATOS DEL TALLER", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 6, f"Nombre: {taller.nombre if taller else 'N/A'}", ln=True)
    pdf.cell(0, 6, f"Direccion: {taller.direccion if taller else 'N/A'}", ln=True)
    pdf.ln(5)
    
    # Datos del Cliente
    cliente = emergencia.cliente
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(0, 8, "DATOS DEL CLIENTE", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 6, f"Nombre: {cliente.nombre}", ln=True)
    pdf.cell(0, 6, f"Email: {cliente.correo}", ln=True)
    pdf.cell(0, 6, f"Vehiculo Placa: {emergencia.placaVehiculo}", ln=True)
    pdf.ln(10)
    
    # Detalle de Items
    pdf.set_font("Helvetica", style="B", size=11)
    
    # Encabezados de tabla
    pdf.cell(90, 8, "Descripcion", border=1)
    pdf.cell(30, 8, "Tipo", border=1, align="C")
    pdf.cell(20, 8, "Cant.", border=1, align="C")
    pdf.cell(25, 8, "Precio Un.", border=1, align="C")
    pdf.cell(25, 8, "Total", border=1, align="C")
    pdf.ln(8)
    
    pdf.set_font("Helvetica", size=10)
    items = detalle.get("items", [])
    
    if not items:
        pdf.cell(165, 8, "Servicio general (Sin desglose)", border=1)
        pdf.cell(25, 8, f"${pago.monto}", border=1, align="C")
        pdf.ln(8)
    else:
        for item in items:
            pdf.cell(90, 8, str(item.get("descripcion", ""))[:45], border=1)
            pdf.cell(30, 8, str(item.get("tipo", "")).capitalize(), border=1, align="C")
            pdf.cell(20, 8, str(item.get("cantidad", "1")), border=1, align="C")
            pdf.cell(25, 8, f"${float(item.get('precio_unitario', 0)):.2f}", border=1, align="R")
            pdf.cell(25, 8, f"${float(item.get('total', 0)):.2f}", border=1, align="R")
            pdf.ln(8)
            
    pdf.ln(10)
    
    # Totales
    subtotal = float(detalle.get("subtotal", pago.monto))
    impuestos = float(detalle.get("impuestos", 0.0))
    total_general = float(detalle.get("total_general", pago.monto))
    
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.cell(140, 8, "", border=0)
    pdf.cell(25, 8, "Subtotal:", border=0, align="R")
    pdf.cell(25, 8, f"${subtotal:.2f}", border=0, align="R")
    pdf.ln(6)
    
    # Mostrar comisión (10%)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(140, 8, "", border=0)
    pdf.cell(25, 8, "Servicio (10%):", border=0, align="R")
    pdf.cell(25, 8, f"${float(pago.monto_comision):.2f}", border=0, align="R")
    pdf.ln(6)

    pdf.set_font("Helvetica", size=10)
    pdf.cell(140, 8, "", border=0)
    pdf.cell(25, 8, "Impuestos:", border=0, align="R")
    pdf.cell(25, 8, f"${impuestos:.2f}", border=0, align="R")
    pdf.ln(6)
    
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(140, 8, "", border=0)
    pdf.cell(25, 8, "TOTAL:", border=0, align="R")
    pdf.cell(25, 8, f"${total_general:.2f}", border=0, align="R")
    
    pdf_bytes = pdf.output()
    
    # Return as PDF file
    return Response(content=bytes(pdf_bytes), media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=factura_{pago.id:06d}.pdf"
    })
