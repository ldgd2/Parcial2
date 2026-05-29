"""
CU05 — Gestionar Tipo de Pago

POST /pagos/{emergencia_id} → Registrar pago de una emergencia finalizada
GET  /pagos/{emergencia_id} → Obtener pago registrado de una emergencia

Regla de negocio:
  - Comisión de plataforma: 10% del monto total del servicio
  - Solo admins del taller al que pertenece la emergencia pueden registrar el pago
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal
import datetime

import stripe
from app.db.session import get_db
from app.core.dependencies import require_role
from app.packages.gestion_administrativa_reportes.modules.pagos.models.pago import Pago
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.emergencia import Emergencia
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.estado import Estado
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.historial_estado import HistorialEstado
from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.services import ai_service
from app.core.config import settings
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.cliente import Cliente
from app.packages.gestion_administrativa_reportes.modules.pagos.models.metodo_pago import MetodoPago
from app.packages.gestion_administrativa_reportes.modules.pagos.schemas.metodo_pago import MetodoPagoOut, SetupIntentOut, MetodoPagoCreate
from app.packages.gestion_administrativa_reportes.modules.pagos.schemas.pago import PagoStripeCreate, PagoOut, PagoCreate
from app.core.socket_manager import manager

stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter(prefix="/pagos", tags=["Comercio — Pagos (CU05)"])


@router.post(
    "/{emergencia_id}",
    response_model=PagoOut,
    status_code=201,
    summary="CU05 — Registrar pago de emergencia (Admin)",
)
async def registrar_pago(
    emergencia_id: int,
    data: PagoCreate,
    current=Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    CU05: Registra el pago del servicio de emergencia (Manual por Admin).
    Calcula automáticamente la comisión del 10% y el monto neto al taller.
    """
    # 1. Verificar que la emergencia existe
    from sqlalchemy.orm import selectinload
    res = await db.execute(
        select(Emergencia).options(selectinload(Emergencia.pago)).where(Emergencia.id == emergencia_id)
    )
    emergencia = res.unique().scalar_one_or_none()
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada.")

    # 2. Verificar que pertenece al taller del admin autenticado
    taller_cod = current.get("taller")
    if emergencia.idTaller != taller_cod:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta emergencia no pertenece a tu taller.",
        )

    # 2. Verificar o Recuperar el Pago
    # Si la emergencia ya tiene un pago vinculado (a través de la relación), lo actualizamos
    pago = emergencia.pago

    # 3. Calcular comisión de plataforma (10%)
    comision = data.monto * Decimal("0.10")

    if pago:
        # Si ya estaba completado con monto > 0, no permitimos re-pagar
        if pago.estado == "COMPLETADO" and pago.monto > 0:
             raise HTTPException(status_code=400, detail="Esta emergencia ya ha sido pagada.")
        
        # Actualizamos el pago existente
        pago.monto = data.monto
        pago.monto_comision = comision
        pago.estado = "COMPLETADO"
        pago.fecha_pago = datetime.date.today()
    else:
        # Si por alguna razón no tiene pago vinculado, creamos uno nuevo
        pago = Pago(
            monto=data.monto,
            monto_comision=comision,
            cliente_id=emergencia.idCliente,
            emergencia_id=emergencia.id,
            estado="COMPLETADO",
            fecha_pago=datetime.date.today(),
        )
        db.add(pago)
        await db.flush()

    # 4. Finalizar emergencia
    # Cambiar estado a FINALIZADA (ID 8 sugerido)
    estado_fin_res = await db.execute(select(Estado).where(Estado.nombre == "FINALIZADA"))
    estado_fin = estado_fin_res.scalar_one_or_none()
    if estado_fin:
        emergencia.idEstado = estado_fin.id
        historial = HistorialEstado(
            idEmergencia=emergencia.id,
            idEstado=estado_fin.id
        )
        db.add(historial)

    await db.commit()
    await db.refresh(pago)
    return pago


# --- STRIPE ENDPOINTS PARA CLIENTES ---

async def _get_or_create_stripe_customer(cliente: Cliente, db: AsyncSession):
    if cliente.stripe_customer_id:
        return cliente.stripe_customer_id
    
    customer = stripe.Customer.create(
        email=cliente.correo,
        name=cliente.nombre,
        metadata={"cliente_id": cliente.id}
    )
    cliente.stripe_customer_id = customer.id
    await db.flush()
    return customer.id

@router.post(
    "/stripe/setup-intent",
    response_model=SetupIntentOut,
    summary="Stripe — Crear Setup Intent para registrar tarjeta",
)
async def create_setup_intent(
    current=Depends(require_role("cliente")),
    db: AsyncSession = Depends(get_db),
):
    """Crea un SetupIntent para que el cliente pueda registrar una tarjeta de forma segura."""
    cliente_res = await db.execute(select(Cliente).where(Cliente.id == current["user_id"]))
    cliente = cliente_res.scalar_one()
    
    customer_id = await _get_or_create_stripe_customer(cliente, db)
    await db.commit()
    
    try:
        intent = stripe.SetupIntent.create(
            customer=customer_id,
            payment_method_types=["card"],
        )
    except stripe.error.StripeError as e:
        print(f"Error de Stripe en SetupIntent: {e}")
        raise HTTPException(status_code=400, detail=f"No se pudo iniciar el registro de tarjeta: {str(e)}")
    
    return {"client_secret": intent.client_secret, "customer_id": customer_id}

@router.post(
    "/stripe/sync-cards",
    response_model=list[MetodoPagoOut],
    summary="Stripe — Sincronizar tarjetas de Stripe a la DB",
)
async def sync_cards(
    current=Depends(require_role("cliente")),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene las tarjetas registradas en Stripe y las sincroniza con nuestra DB."""
    cliente_res = await db.execute(select(Cliente).where(Cliente.id == current["user_id"]))
    cliente = cliente_res.scalar_one()
    
    if not cliente.stripe_customer_id:
        return []

    # Listar métodos de pago del cliente en Stripe
    pms = stripe.PaymentMethod.list(
        customer=cliente.stripe_customer_id,
        type="card",
    )
    
    saved_methods = []
    for pm in pms.data:
        # Verificar si ya lo tenemos
        res = await db.execute(
            select(MetodoPago).where(MetodoPago.stripe_payment_method_id == pm.id)
        )
        existing = res.scalar_one_or_none()
        
        if not existing:
            new_pm = MetodoPago(
                cliente_id=cliente.id,
                stripe_payment_method_id=pm.id,
                marca=pm.card.brand,
                ultimo4=pm.card.last4,
            )
            db.add(new_pm)
            saved_methods.append(new_pm)
        else:
            saved_methods.append(existing)
            
    await db.commit()
    return saved_methods

@router.post(
    "/stripe/confirm-card",
    response_model=MetodoPagoOut,
    summary="Stripe — Confirmar y guardar tarjeta en DB",
)
async def confirm_card(
    data: MetodoPagoCreate,
    current=Depends(require_role("cliente")),
    db: AsyncSession = Depends(get_db),
):
    """Guarda el payment_method_id de Stripe en nuestra base de datos local."""
    try:
        payment_method_id = data.stripe_payment_method_id
        
        # 1. Verificar si ya existe para este usuario
        res = await db.execute(
            select(MetodoPago).where(
                MetodoPago.stripe_payment_method_id == payment_method_id
            )
        )
        if res.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Esta tarjeta ya está registrada.")

        # 2. Obtener detalles de la tarjeta desde Stripe (Sincrónico, pero manejamos el error)
        try:
            pm = stripe.PaymentMethod.retrieve(payment_method_id)
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=f"Error de Stripe: {str(e)}")
        
        nuevo_metodo = MetodoPago(
            cliente_id=current["user_id"],
            stripe_payment_method_id=payment_method_id,
            marca=pm.card.brand,
            ultimo4=pm.card.last4,
        )
        db.add(nuevo_metodo)
        await db.commit()
        await db.refresh(nuevo_metodo)
        return nuevo_metodo
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"Error inesperado al confirmar tarjeta: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno al procesar la tarjeta.")

@router.get(
    "/stripe/metodos",
    response_model=list[MetodoPagoOut],
    summary="Stripe — Listar tarjetas guardadas",
)
async def listar_metodos_pago(
    current=Depends(require_role("cliente")),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(select(MetodoPago).where(MetodoPago.cliente_id == current["user_id"]))
    return res.scalars().all()

@router.post(
    "/stripe/create-intent",
    response_model=PagoOut,
    summary="Stripe — Crear Payment Intent para pagar emergencia",
)
async def create_payment_intent(
    data: PagoStripeCreate,
    current=Depends(require_role("cliente")),
    db: AsyncSession = Depends(get_db),
):
    """
    Crea un PaymentIntent de Stripe.
    Calcula el 10% de comisión y lo guarda en la DB.
    """
    cliente_res = await db.execute(select(Cliente).where(Cliente.id == current["user_id"]))
    cliente = cliente_res.scalar_one()
    
    emergencia_res = await db.execute(select(Emergencia).where(Emergencia.id == data.emergencia_id))
    emergencia = emergencia_res.scalar_one_or_none()
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada")

    # Verificar si ya existe un pago completado
    pago_existente = await db.execute(
        select(Pago).where(Pago.emergencia_id == data.emergencia_id, Pago.estado == "COMPLETADO")
    )
    if pago_existente.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Esta emergencia ya ha sido pagada.")

    # Calcular comisión 10%
    comision = data.monto * Decimal("0.10")
    
    # Stripe requiere el monto en centavos (int)
    amount_cents = int(data.monto * 100)
    
    customer_id = await _get_or_create_stripe_customer(cliente, db)
    
    # Crear el Payment Intent en Stripe
    intent_params = {
        "amount": amount_cents,
        "currency": "usd",
        "customer": customer_id,
        "metadata": {
            "emergencia_id": emergencia.id,
            "cliente_id": cliente.id,
            "comision": str(comision)
        }
    }
    
    if data.metodo_pago_id:
        intent_params["payment_method"] = data.metodo_pago_id
        intent_params["off_session"] = True
        intent_params["confirm"] = True
    
    try:
        intent = stripe.PaymentIntent.create(**intent_params)
    except stripe.error.StripeError as e:
        print(f"Error de Stripe al crear Intent: {e}")
        raise HTTPException(status_code=400, detail=f"Error en el pago: {str(e)}")
    except Exception as e:
        print(f"Error inesperado en create_payment_intent: {e}")
        raise HTTPException(status_code=500, detail="Error interno al procesar el pago.")
    
    # Crear registro de pago en DB (Estado PENDIENTE hasta que se confirme)
    pago = Pago(
        monto=data.monto,
        monto_comision=comision,
        cliente_id=cliente.id,
        emergencia_id=emergencia.id,
        stripe_intent_id=intent.id,
        metodo_pago_id=data.metodo_pago_id,
        estado="COMPLETADO" if intent.status == "succeeded" else "PENDIENTE",
        fecha_pago=datetime.date.today(),
    )
    db.add(pago)
    await db.flush()
    
    emergencia.idPago = pago.id
    
    # Si el pago ya se completó (succeeded), marcamos como FINALIZADA
    if intent.status == "succeeded":
        estado_fin_res = await db.execute(select(Estado).where(Estado.nombre == "FINALIZADA"))
        estado_fin = estado_fin_res.scalar_one_or_none()
        if estado_fin:
            emergencia.idEstado = estado_fin.id
            historial = HistorialEstado(
                idEmergencia=emergencia.id,
                idEstado=estado_fin.id
            )
            db.add(historial)
            
            # Notificar via WebSocket
            await manager.send_personal_message({
                "type": "pago_completado",
                "emergencia_id": emergencia.id,
                "monto": str(pago.monto)
            }, str(cliente.id))

    await db.commit()
    await db.refresh(pago)
    
    return pago


@router.get(
    "/{emergencia_id}",
    response_model=PagoOut,
    summary="CU05 — Obtener pago de una emergencia",
)
async def obtener_pago(
    emergencia_id: int,
    current=Depends(require_role("admin", "cliente", "tecnico")),
    db: AsyncSession = Depends(get_db),
):
    """Retorna el registro de pago asociado a la emergencia, si existe."""
    # 1. Verificar que la emergencia existe (query simple, sin relaciones)
    emg_res = await db.execute(select(Emergencia).where(Emergencia.id == emergencia_id))
    emergencia = emg_res.scalar_one_or_none()
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada")

    # 2. Seguridad: Validar propiedad según el rol
    if current["role"] == "cliente" and emergencia.idCliente != current["user_id"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este pago")
    elif current["role"] == "tecnico" and emergencia.idTaller != current.get("taller"):
        raise HTTPException(status_code=403, detail="Esta emergencia no pertenece a tu taller")

    # 3. Obtener el pago directamente de la tabla Pago (evita problemas de relación)
    # Si hay múltiples pagos (ej. uno inicial en $0 y el real), tomamos el más reciente
    pago_res = await db.execute(
        select(Pago)
        .where(Pago.emergencia_id == emergencia_id)
        .order_by(Pago.id.desc())
    )
    pago = pago_res.scalars().first()

    if not pago:
        raise HTTPException(status_code=404, detail="Pago no registrado para esta emergencia")

    return pago
