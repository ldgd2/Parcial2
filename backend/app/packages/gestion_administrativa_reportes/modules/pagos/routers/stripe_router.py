import os
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.suscripcion import PlanSuscripcion

from app.core.config import settings

router = APIRouter(prefix="/stripe", tags=["Pagos"])

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentIntentRequest(BaseModel):
    plan_id: int

@router.get("/config")
async def get_stripe_config():
    """Retorna la clave pública de Stripe para inicializar Elements en el frontend"""
    return {"publishableKey": settings.STRIPE_PUBLIC_KEY}

@router.post("/create-payment-intent")
async def create_payment_intent(request: PaymentIntentRequest, db: AsyncSession = Depends(get_db)):
    try:
        plan = await db.get(PlanSuscripcion, request.plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan no encontrado")
        
        monto = int(plan.precio_mensual * 100) # Stripe espera centavos
        
        if monto <= 0:
            return {"clientSecret": None, "message": "Plan gratuito, no requiere pago"}

        intent = stripe.PaymentIntent.create(
            amount=monto,
            currency="usd",
            automatic_payment_methods={"enabled": True},
        )
        return {"clientSecret": intent.client_secret}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
