"""
Plataforma Inteligente de Atención de Emergencias Vehiculares
Backend FastAPI — Punto de entrada principal

Arquitectura de paquetes (Ciclo 3):
  ┌─────────────────────────────────────────────────────────────────┐
  │  PAQUETE                  │  CASOS DE USO                       │
  ├───────────────────────────┼─────────────────────────────────────┤
  │  perfil_seguridad         │  CU01 CU02 CU03 CU06 CU07 CU13     │
  │  gestion_ia               │  CU04 CU08 CU09 CU10 CU11 CU12     │
  │  gestion_comercio         │  CU05 CU14 CU15                     │
  └───────────────────────────┴─────────────────────────────────────┘
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.db.session import engine, Base
from app.core.audit import register_audit_listeners
from app.core.context import set_ip_context, set_user_context
from fastapi import Request

# ─── Importar todos los modelos para que Alembic los detecte ──────
from app.db.base import *  # Import the centralized orchestrator

# ─── Paquetes de la nueva arquitectura ────────────────────────────
from app.packages.gestion_usuarios_seguridad.router import router as p1_router
from app.packages.gestion_emergencias_solicitudes.router import router as p2_router
from app.packages.inteligencia_artificial_automatizacion.router import router as p3_router
from app.packages.gestion_administrativa_reportes.router import router as p4_router

# ─── Inicializar Auditoría Universal ────────────────────────────
register_audit_listeners(Base)

app = FastAPI(
    title=settings.APP_NAME,
    version="3.0.0",
    description="""
## Plataforma de Emergencias Vehiculares — Arquitectura Modular (DDD)

### Arquitectura de Paquetes

| Paquete | Responsabilidad |
|---|---|
| **Gestión Usuarios y Seguridad** | Autenticación, Usuarios, Técnicos, Talleres |
| **Gestión Emergencias y Solicitudes** | Emergencias, Auxilio, Cotizaciones |
| **IA y Automatización** | Clasificación, Asignación, Notificaciones |
| **Administrativa y Reportes** | Pagos, KPI, Facturación |
    """,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── Configuración Almacenamiento Multimedia (Storage) ────────────
UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# ─── Idempotency Middleware ───────────────────────────────────────
from app.core.idempotency_middleware import IdempotencyMiddleware
app.add_middleware(IdempotencyMiddleware)

# ─── CORS ─────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "http://localhost:4042",
        "http://185.214.134.23:4042",
        "http://185.214.134.23:4200",
        "http://185.214.134.23"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Middleware de Contexto (IP y Usuario) ───────────────────────
@app.middleware("http")
async def context_middleware(request: Request, call_next):
    # Capturar IP del cliente
    ip = request.client.host if request.client else "unknown"
    set_ip_context(ip)
    
    # Reset user context for each request
    set_user_context(None)
    
    response = await call_next(request)
    return response

# ─── Registrar paquetes ───────────────────────────────────────────
PREFIX = settings.API_V1_PREFIX

# Paquete 1: Gestión Perfil y Seguridad
app.include_router(p1_router, prefix=PREFIX)

# Paquete 2: Gestión Emergencias y Solicitudes
app.include_router(p2_router, prefix=PREFIX)

# Paquete 3: IA y Automatización
app.include_router(p3_router, prefix=PREFIX)

# Paquete 4: Gestión Administrativa y Reportes
app.include_router(p4_router, prefix=PREFIX)


@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "version": "3.0.0",
        "paquetes": ["perfil_seguridad", "gestion_ia", "gestion_comercio"],
        "message": "Plataforma de Emergencias Vehiculares operativa."
    }
