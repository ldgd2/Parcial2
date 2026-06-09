from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from pydantic import BaseModel, EmailStr

from app.db.session import get_db
from app.core.dependencies import require_role
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.usuario import Usuario
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.tecnico import Tecnico
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.suscripcion import PlanSuscripcion
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.permisos import Rol

router = APIRouter()

# ── Schemas ────────────────────────────────────────────────────────────────────

class PlanOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    precio_mensual: float
    max_sucursales: int
    max_tecnicos: int
    max_admins_sucursal: int

class TenantSchema(BaseModel):
    cod: str
    nombre: str
    direccion: str
    estado: str
    plan_id: Optional[int] = None
    plan_nombre: Optional[str] = None
    admin_correo: Optional[str] = None
    total_usuarios: Optional[int] = 0
    total_tecnicos: Optional[int] = 0

class TenantCreateSchema(BaseModel):
    nombre: str
    direccion: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    plan_id: Optional[int] = None
    admin_nombre: Optional[str] = None
    admin_apellido: Optional[str] = None
    admin_correo: Optional[str] = None
    admin_contrasena: Optional[str] = None

class TenantUpdateSchema(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    plan_id: Optional[int] = None

class TenantStatusUpdateSchema(BaseModel):
    estado: str

class SaasStatsSchema(BaseModel):
    total_tenants: int
    tenants_activos: int
    tenants_suspendidos: int
    tenants_cancelados: int
    total_usuarios: int
    total_tecnicos: int
    ingresos_mensuales: float

class TenantUserOut(BaseModel):
    id: int
    nombre: str
    apellido: Optional[str] = None
    correo: str
    telefono: Optional[str] = None
    estado: str
    tipo: str  # ADMINISTRATIVO | TECNICO
    rol_nombre: Optional[str] = None

class TenantUserCreate(BaseModel):
    nombre: str
    apellido: Optional[str] = None
    correo: str
    contrasena: str
    rol_id: int
    telefono: Optional[str] = None

class TenantUserStatus(BaseModel):
    estado: str

class TenantUserResetPassword(BaseModel):
    nueva_contrasena: str

# ── Auth guard ─────────────────────────────────────────────────────────────────

def require_super_admin(current_user: dict = Depends(require_role("admin", "admin_sucursal"))):
    if current_user.get("taller") != "GLOBAL":
        raise HTTPException(status_code=403, detail="Permiso denegado. Solo Super Admin.")
    return current_user

# ── Helpers ────────────────────────────────────────────────────────────────────

async def _build_tenant_schema(db: AsyncSession, t: Taller) -> TenantSchema:
    admin_correo = None
    admin_result = await db.execute(
        select(Usuario).filter_by(idTaller=t.cod).limit(1)
    )
    admin = admin_result.scalar_one_or_none()
    if admin:
        admin_correo = admin.correo

    plan_nombre = None
    if t.plan_id:
        plan = await db.get(PlanSuscripcion, t.plan_id)
        if plan:
            plan_nombre = plan.nombre

    usuarios_count = (await db.execute(
        select(func.count()).select_from(Usuario).filter_by(idTaller=t.cod)
    )).scalar() or 0

    tecnicos_count = (await db.execute(
        select(func.count()).select_from(Tecnico).filter_by(idTaller=t.cod)
    )).scalar() or 0

    return TenantSchema(
        cod=t.cod,
        nombre=t.nombre,
        direccion=t.direccion,
        estado=t.estado,
        plan_id=t.plan_id,
        plan_nombre=plan_nombre,
        admin_correo=admin_correo,
        total_usuarios=usuarios_count,
        total_tecnicos=tecnicos_count,
    )

# ── Planes ─────────────────────────────────────────────────────────────────────

@router.get("/planes", response_model=List[PlanOut])
async def listar_planes(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    result = await db.execute(select(PlanSuscripcion).order_by(PlanSuscripcion.precio_mensual))
    planes = result.scalars().all()
    return [
        PlanOut(
            id=p.id,
            nombre=p.nombre,
            descripcion=p.descripcion,
            precio_mensual=p.precio_mensual,
            max_sucursales=p.max_sucursales,
            max_tecnicos=p.max_tecnicos,
            max_admins_sucursal=p.max_admins_sucursal,
        )
        for p in planes
    ]

# ── Stats ──────────────────────────────────────────────────────────────────────

@router.get("/stats", response_model=SaasStatsSchema)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    talleres = (await db.execute(select(Taller))).scalars().all()

    activos = sum(1 for t in talleres if t.estado == "ACTIVO")
    suspendidos = sum(1 for t in talleres if t.estado == "SUSPENDIDO")
    cancelados = sum(1 for t in talleres if t.estado == "CANCELADO")

    total_usuarios = (await db.execute(
        select(func.count()).select_from(Usuario)
    )).scalar() or 0

    total_tecnicos = (await db.execute(
        select(func.count()).select_from(Tecnico)
    )).scalar() or 0

    # Ingresos estimados: sumar precio_mensual de plan de cada taller activo
    planes_cache: dict[int, float] = {}
    ingresos = 0.0
    for t in talleres:
        if t.estado == "ACTIVO" and t.plan_id:
            if t.plan_id not in planes_cache:
                plan = await db.get(PlanSuscripcion, t.plan_id)
                planes_cache[t.plan_id] = plan.precio_mensual if plan else 0.0
            ingresos += planes_cache[t.plan_id]

    return SaasStatsSchema(
        total_tenants=len(talleres),
        tenants_activos=activos,
        tenants_suspendidos=suspendidos,
        tenants_cancelados=cancelados,
        total_usuarios=total_usuarios,
        total_tecnicos=total_tecnicos,
        ingresos_mensuales=ingresos,
    )

# ── Tenants CRUD ───────────────────────────────────────────────────────────────

@router.get("/", response_model=List[TenantSchema])
async def listar_tenants(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    result = await db.execute(select(Taller).order_by(Taller.nombre))
    talleres = result.scalars().all()
    return [await _build_tenant_schema(db, t) for t in talleres]


@router.post("/", response_model=TenantSchema)
async def crear_tenant(
    payload: TenantCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    import uuid
    new_cod = "T-" + str(uuid.uuid4())[:8].upper()

    nuevo_taller = Taller(
        cod=new_cod,
        nombre=payload.nombre,
        direccion=payload.direccion,
        latitud=payload.latitud or 0.0,
        longitud=payload.longitud or 0.0,
        estado="ACTIVO",
        plan_id=payload.plan_id
    )
    db.add(nuevo_taller)
    await db.commit()
    await db.refresh(nuevo_taller)

    if payload.admin_correo:
        from app.core.security import hash_password
        stmt_rol = select(Rol).where(Rol.nombre == "ADMIN_TALLER")
        rol = (await db.execute(stmt_rol)).scalar_one_or_none()
        nuevo_admin = Usuario(
            nombre=payload.admin_nombre or "Admin",
            apellido=payload.admin_apellido or "Taller",
            correo=payload.admin_correo,
            contrasena=hash_password(payload.admin_contrasena or "Admin123!"),
            estado="ACTIVO",
            idTaller=nuevo_taller.cod,
            id_rol=rol.id if rol else None
        )
        db.add(nuevo_admin)
        await db.commit()

    return await _build_tenant_schema(db, nuevo_taller)


@router.get("/{cod}", response_model=TenantSchema)
async def obtener_tenant(
    cod: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    taller = await Taller.get_by_cod(db, cod)
    if not taller:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    return await _build_tenant_schema(db, taller)


@router.put("/{cod}", response_model=TenantSchema)
async def editar_tenant(
    cod: str,
    payload: TenantUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    taller = await Taller.get_by_cod(db, cod)
    if not taller:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")

    if payload.nombre is not None:
        taller.nombre = payload.nombre
    if payload.direccion is not None:
        taller.direccion = payload.direccion
    if payload.plan_id is not None:
        taller.plan_id = payload.plan_id

    await db.commit()
    await db.refresh(taller)
    return await _build_tenant_schema(db, taller)


@router.patch("/{cod}/status", response_model=TenantSchema)
async def cambiar_estado_tenant(
    cod: str,
    payload: TenantStatusUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    if payload.estado not in ["ACTIVO", "SUSPENDIDO", "CANCELADO"]:
        raise HTTPException(status_code=400, detail="Estado inválido")

    taller = await Taller.get_by_cod(db, cod)
    if not taller:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")

    taller.estado = payload.estado
    await db.commit()
    await db.refresh(taller)
    return await _build_tenant_schema(db, taller)

# ── Tenant Users (super admin view) ───────────────────────────────────────────

@router.get("/{cod}/usuarios", response_model=List[TenantUserOut])
async def listar_usuarios_de_tenant(
    cod: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    taller = await Taller.get_by_cod(db, cod)
    if not taller:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")

    usuarios_result = await db.execute(
        select(Usuario, Rol).outerjoin(Rol, Usuario.id_rol == Rol.id)
        .filter(Usuario.idTaller == cod)
    )
    tecnicos_result = await db.execute(
        select(Tecnico).filter(Tecnico.idTaller == cod)
    )

    out: List[TenantUserOut] = []
    for usuario, rol in usuarios_result.all():
        out.append(TenantUserOut(
            id=usuario.id,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            correo=usuario.correo,
            telefono=None,
            estado=usuario.estado,
            tipo="ADMINISTRATIVO",
            rol_nombre=rol.nombre if rol else None,
        ))

    for tecnico in tecnicos_result.scalars().all():
        out.append(TenantUserOut(
            id=tecnico.id,
            nombre=tecnico.nombre,
            apellido=None,
            correo=tecnico.correo,
            telefono=tecnico.telefono,
            estado=tecnico.estado,
            tipo="TECNICO",
            rol_nombre="TECNICO",
        ))

    return out


@router.post("/{cod}/usuarios", response_model=TenantUserOut)
async def crear_usuario_en_tenant(
    cod: str,
    payload: TenantUserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    taller = await Taller.get_by_cod(db, cod)
    if not taller:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")

    from app.core.security import hash_password

    rol = await db.get(Rol, payload.rol_id)
    if not rol:
        raise HTTPException(status_code=400, detail="Rol no encontrado")

    is_tecnico = rol.nombre in ["MECANICO", "TECNICO"]

    if is_tecnico:
        if not payload.telefono:
            raise HTTPException(status_code=400, detail="El teléfono es requerido para técnicos")
        nuevo = Tecnico(
            nombre=payload.nombre,
            correo=payload.correo,
            contrasena=hash_password(payload.contrasena),
            telefono=payload.telefono,
            estado="ACTIVO",
            idTaller=cod,
        )
        db.add(nuevo)
        await db.commit()
        await db.refresh(nuevo)
        return TenantUserOut(
            id=nuevo.id, nombre=nuevo.nombre, apellido=None,
            correo=nuevo.correo, telefono=nuevo.telefono,
            estado=nuevo.estado, tipo="TECNICO", rol_nombre=rol.nombre,
        )
    else:
        nuevo = Usuario(
            nombre=payload.nombre,
            apellido=payload.apellido,
            correo=payload.correo,
            contrasena=hash_password(payload.contrasena),
            estado="ACTIVO",
            idTaller=cod,
            id_rol=rol.id,
        )
        db.add(nuevo)
        await db.commit()
        await db.refresh(nuevo)
        return TenantUserOut(
            id=nuevo.id, nombre=nuevo.nombre, apellido=nuevo.apellido,
            correo=nuevo.correo, telefono=None,
            estado=nuevo.estado, tipo="ADMINISTRATIVO", rol_nombre=rol.nombre,
        )


@router.patch("/{cod}/usuarios/{tipo}/{id}/status")
async def cambiar_estado_usuario_tenant(
    cod: str,
    tipo: str,
    id: int,
    payload: TenantUserStatus,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    if tipo not in ["TECNICO", "ADMINISTRATIVO"]:
        raise HTTPException(status_code=400, detail="Tipo inválido")
    if payload.estado not in ["ACTIVO", "INACTIVO"]:
        raise HTTPException(status_code=400, detail="Estado inválido")

    if tipo == "TECNICO":
        obj = await db.get(Tecnico, id)
        if not obj or obj.idTaller != cod:
            raise HTTPException(status_code=404, detail="Técnico no encontrado en este tenant")
    else:
        obj = await db.get(Usuario, id)
        if not obj or obj.idTaller != cod:
            raise HTTPException(status_code=404, detail="Usuario no encontrado en este tenant")

    obj.estado = payload.estado
    await db.commit()
    return {"ok": True, "estado": payload.estado}


@router.patch("/{cod}/usuarios/{tipo}/{id}/reset-password")
async def reset_password_usuario_tenant(
    cod: str,
    tipo: str,
    id: int,
    payload: TenantUserResetPassword,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    if tipo not in ["TECNICO", "ADMINISTRATIVO"]:
        raise HTTPException(status_code=400, detail="Tipo inválido")

    from app.core.security import hash_password

    if tipo == "TECNICO":
        obj = await db.get(Tecnico, id)
        if not obj or obj.idTaller != cod:
            raise HTTPException(status_code=404, detail="Técnico no encontrado en este tenant")
    else:
        obj = await db.get(Usuario, id)
        if not obj or obj.idTaller != cod:
            raise HTTPException(status_code=404, detail="Usuario no encontrado en este tenant")

    obj.contrasena = hash_password(payload.nueva_contrasena)
    await db.commit()
    return {"ok": True}
