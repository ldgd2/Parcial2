"""
Super Admin — Endpoints de control del sistema.
Acceso exclusivo: SUPER_ADMIN (taller == GLOBAL).
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from typing import List, Optional, Any, Dict
from pydantic import BaseModel
from datetime import datetime, timezone

from app.db.session import get_db
from app.core.dependencies import require_role
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.usuario import Usuario
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.tecnico import Tecnico
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.suscripcion import PlanSuscripcion
from app.packages.gestion_administrativa_reportes.modules.reportes_kpis.models.bitacora import Bitacora

router = APIRouter()

# ── Auth guard ─────────────────────────────────────────────────────────────────

def require_super_admin(current_user: dict = Depends(require_role("super_admin"))):
    if current_user.get("taller") != "GLOBAL":
        raise HTTPException(status_code=403, detail="Solo Super Admin.")
    return current_user

# ── Restricciones en memoria ───────────────────────────────────────────────────
# Se resetea al reiniciar el servidor. Para persistencia real se necesita una tabla.
_restricciones: Dict[str, Any] = {
    "registro_publico_habilitado": True,
    "nuevos_talleres_habilitados": True,
    "modo_mantenimiento": False,
    "max_emergencias_simultaneas": 100,
    "notificaciones_push_habilitadas": True,
    "ia_clasificacion_habilitada": True,
    "stripe_habilitado": True,
    "logs_verboso": False,
}

# ── Schemas ────────────────────────────────────────────────────────────────────

class SaludSistema(BaseModel):
    estado: str
    db_conectada: bool
    total_talleres: int
    total_usuarios: int
    total_tecnicos: int
    version: str
    timestamp: str

class BitacoraOut(BaseModel):
    id: int
    accion: str
    tabla: Optional[str] = None
    registro_id: Optional[str] = None
    ip: Optional[str] = None
    fecha: Optional[str] = None
    idUsuario: Optional[int] = None

class RestriccionesSchema(BaseModel):
    registro_publico_habilitado: bool
    nuevos_talleres_habilitados: bool
    modo_mantenimiento: bool
    max_emergencias_simultaneas: int
    notificaciones_push_habilitadas: bool
    ia_clasificacion_habilitada: bool
    stripe_habilitado: bool
    logs_verboso: bool

class RestriccionUpdate(BaseModel):
    clave: str
    valor: Any

# ── Plan schemas ───────────────────────────────────────────────────────────────

class PlanCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio_mensual: float = 0.0
    max_sucursales: int = 1
    max_tecnicos: int = 5
    max_admins_sucursal: int = 1

class PlanUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_mensual: Optional[float] = None
    max_sucursales: Optional[int] = None
    max_tecnicos: Optional[int] = None
    max_admins_sucursal: Optional[int] = None

class PlanOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    precio_mensual: float
    max_sucursales: int
    max_tecnicos: int
    max_admins_sucursal: int
    total_talleres: Optional[int] = 0

# ── SALUD DEL SISTEMA ──────────────────────────────────────────────────────────

@router.get("/salud", response_model=SaludSistema)
async def salud_sistema(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    total_talleres = (await db.execute(select(func.count()).select_from(Taller))).scalar() or 0
    total_usuarios = (await db.execute(select(func.count()).select_from(Usuario))).scalar() or 0
    total_tecnicos = (await db.execute(select(func.count()).select_from(Tecnico))).scalar() or 0

    return SaludSistema(
        estado="operativo" if db_ok else "degradado",
        db_conectada=db_ok,
        total_talleres=total_talleres,
        total_usuarios=total_usuarios,
        total_tecnicos=total_tecnicos,
        version="3.0.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

# ── AUDIT LOG ─────────────────────────────────────────────────────────────────

@router.get("/audit-log", response_model=List[BitacoraOut])
async def listar_audit_log(
    limit: int = 100,
    offset: int = 0,
    accion: Optional[str] = None,
    tabla: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    stmt = select(Bitacora).order_by(Bitacora.fecha.desc()).offset(offset).limit(min(limit, 500))
    if accion:
        stmt = stmt.where(Bitacora.accion == accion.upper())
    if tabla:
        stmt = stmt.where(Bitacora.tabla == tabla)

    rows = (await db.execute(stmt)).scalars().all()
    return [
        BitacoraOut(
            id=r.id,
            accion=r.accion,
            tabla=r.tabla,
            registro_id=r.registro_id,
            ip=r.ip,
            fecha=r.fecha.isoformat() if r.fecha else None,
            idUsuario=r.idUsuario,
        )
        for r in rows
    ]

# ── RESTRICCIONES ─────────────────────────────────────────────────────────────

@router.get("/restricciones", response_model=RestriccionesSchema)
async def obtener_restricciones(
    current_user: dict = Depends(require_super_admin)
):
    return RestriccionesSchema(**_restricciones)


@router.put("/restricciones", response_model=RestriccionesSchema)
async def actualizar_restricciones(
    payload: RestriccionesSchema,
    current_user: dict = Depends(require_super_admin)
):
    global _restricciones
    _restricciones = payload.model_dump()
    return RestriccionesSchema(**_restricciones)


@router.patch("/restricciones", response_model=RestriccionesSchema)
async def actualizar_restriccion_individual(
    payload: RestriccionUpdate,
    current_user: dict = Depends(require_super_admin)
):
    if payload.clave not in _restricciones:
        raise HTTPException(status_code=400, detail=f"Clave '{payload.clave}' no existe en restricciones.")
    _restricciones[payload.clave] = payload.valor
    return RestriccionesSchema(**_restricciones)

# ── PLANES CRUD ───────────────────────────────────────────────────────────────

@router.get("/planes", response_model=List[PlanOut])
async def listar_planes(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    planes = (await db.execute(select(PlanSuscripcion).order_by(PlanSuscripcion.precio_mensual))).scalars().all()
    result = []
    for p in planes:
        count = (await db.execute(
            select(func.count()).select_from(Taller).where(Taller.plan_id == p.id)
        )).scalar() or 0
        result.append(PlanOut(
            id=p.id, nombre=p.nombre, descripcion=p.descripcion,
            precio_mensual=p.precio_mensual, max_sucursales=p.max_sucursales,
            max_tecnicos=p.max_tecnicos, max_admins_sucursal=p.max_admins_sucursal,
            total_talleres=count,
        ))
    return result


@router.post("/planes", response_model=PlanOut)
async def crear_plan(
    payload: PlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    existing = (await db.execute(select(PlanSuscripcion).where(PlanSuscripcion.nombre == payload.nombre))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un plan con ese nombre.")
    nuevo = PlanSuscripcion(**payload.model_dump())
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    return PlanOut(
        id=nuevo.id, nombre=nuevo.nombre, descripcion=nuevo.descripcion,
        precio_mensual=nuevo.precio_mensual, max_sucursales=nuevo.max_sucursales,
        max_tecnicos=nuevo.max_tecnicos, max_admins_sucursal=nuevo.max_admins_sucursal,
        total_talleres=0,
    )


@router.put("/planes/{plan_id}", response_model=PlanOut)
async def editar_plan(
    plan_id: int,
    payload: PlanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    plan = await db.get(PlanSuscripcion, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado.")
    for campo, valor in payload.model_dump(exclude_none=True).items():
        setattr(plan, campo, valor)
    await db.commit()
    await db.refresh(plan)
    count = (await db.execute(
        select(func.count()).select_from(Taller).where(Taller.plan_id == plan.id)
    )).scalar() or 0
    return PlanOut(
        id=plan.id, nombre=plan.nombre, descripcion=plan.descripcion,
        precio_mensual=plan.precio_mensual, max_sucursales=plan.max_sucursales,
        max_tecnicos=plan.max_tecnicos, max_admins_sucursal=plan.max_admins_sucursal,
        total_talleres=count,
    )


@router.delete("/planes/{plan_id}")
async def eliminar_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    plan = await db.get(PlanSuscripcion, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado.")
    count = (await db.execute(
        select(func.count()).select_from(Taller).where(Taller.plan_id == plan_id)
    )).scalar() or 0
    if count > 0:
        raise HTTPException(status_code=400, detail=f"No se puede eliminar: {count} taller(es) usa(n) este plan.")
    await db.delete(plan)
    await db.commit()
    return {"ok": True}

# ── BACKUP / EXPORTAR ─────────────────────────────────────────────────────────

@router.get("/exportar/{cod}")
async def exportar_tenant(
    cod: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    """Exporta toda la información de un tenant como JSON descargable."""
    taller = (await db.execute(select(Taller).where(Taller.cod == cod))).scalar_one_or_none()
    if not taller:
        raise HTTPException(status_code=404, detail="Tenant no encontrado.")

    usuarios = (await db.execute(select(Usuario).where(Usuario.idTaller == cod))).scalars().all()
    tecnicos = (await db.execute(select(Tecnico).where(Tecnico.idTaller == cod))).scalars().all()

    payload = {
        "exportado_en": datetime.now(timezone.utc).isoformat(),
        "taller": {
            "cod": taller.cod, "nombre": taller.nombre,
            "direccion": taller.direccion, "estado": taller.estado,
            "plan_id": taller.plan_id,
        },
        "usuarios": [
            {"id": u.id, "nombre": u.nombre, "apellido": u.apellido,
             "correo": u.correo, "estado": u.estado}
            for u in usuarios
        ],
        "tecnicos": [
            {"id": t.id, "nombre": t.nombre, "correo": t.correo,
             "telefono": t.telefono, "estado": t.estado}
            for t in tecnicos
        ],
    }
    filename = f"backup_{cod}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    return JSONResponse(
        content=payload,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/exportar-global")
async def exportar_global(
    current_user: dict = Depends(require_super_admin)
):
    """Exporta la base de datos completa como archivo binario de PostgreSQL (pg_dump custom format)."""
    import os
    import subprocess
    import tempfile
    from fastapi.responses import FileResponse
    from starlette.background import BackgroundTask
    from app.core.config import settings

    # Crear un archivo temporal para el volcado
    fd, filepath = tempfile.mkstemp(suffix=".backup", prefix="global_backup_")
    os.close(fd)

    try:
        # Configurar variables de entorno para la contraseña
        env = os.environ.copy()
        env["PGPASSWORD"] = settings.DB_PASSWORD

        # Comando pg_dump: -F c = Formato Custom (binario compatible con pg_restore)
        comando = [
            "pg_dump",
            "-h", settings.DB_HOST,
            "-p", str(settings.DB_PORT),
            "-U", settings.DB_USER,
            "-F", "c",
            "-f", filepath,
            settings.DB_NAME
        ]

        proceso = subprocess.run(
            comando,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if proceso.returncode != 0:
            os.remove(filepath)
            print(f"Error en pg_dump: {proceso.stderr}")
            raise HTTPException(status_code=500, detail="Error al generar el respaldo binario de la base de datos.")

        filename = f"backup_global_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.backup"
        
        # Enviar archivo y eliminarlo después de que se envíe (BackgroundTask)
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type="application/octet-stream",
            background=BackgroundTask(os.remove, filepath)
        )

    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        raise HTTPException(status_code=500, detail=str(e))
