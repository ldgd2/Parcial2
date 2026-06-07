from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel, EmailStr

from app.db.session import get_db
from app.core.dependencies import require_role
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.usuario import Usuario

router = APIRouter()

class TenantSchema(BaseModel):
    cod: str
    nombre: str
    direccion: str
    estado: str
    plan_id: Optional[int] = None
    admin_correo: Optional[str] = None

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

def require_super_admin(current_user: dict = Depends(require_role("admin", "admin_sucursal"))):
    if current_user.get("taller") != "GLOBAL":
        raise HTTPException(status_code=403, detail="Permiso denegado. Solo Super Admin.")
    return current_user

# Endpoints for SUPER_ADMIN

@router.get("/", response_model=List[TenantSchema])
async def listar_tenants(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    """Lista todos los tenants del sistema (SaaS)"""
    result = await db.execute(select(Taller))
    talleres = result.scalars().all()
    
    response = []
    for t in talleres:
        # Encontrar el correo del admin (primer usuario de ese taller)
        admin_correo = None
        admin_result = await db.execute(select(Usuario).filter_by(idTaller=t.cod).limit(1))
        admin = admin_result.scalar_one_or_none()
        if admin:
            admin_correo = admin.correo

        response.append(TenantSchema(
            cod=t.cod,
            nombre=t.nombre,
            direccion=t.direccion,
            estado=t.estado,
            plan_id=t.plan_id,
            admin_correo=admin_correo
        ))
    return response


@router.post("/", response_model=TenantSchema)
async def crear_tenant(
    payload: TenantCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    """Crea un nuevo tenant (Taller)"""
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
    
    # Crear AdminTaller
    if payload.admin_correo and payload.admin_contrasena:
        from app.core.security import hash_password
        from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.permisos import Rol
        
        stmt_rol = select(Rol).where(Rol.nombre == "ADMIN_TALLER")
        rol = (await db.execute(stmt_rol)).scalar_one_or_none()
        
        nuevo_admin = Usuario(
            nombre=payload.admin_nombre or "Admin",
            apellido=payload.admin_apellido or "Taller",
            correo=payload.admin_correo,
            contrasena=hash_password(payload.admin_contrasena),
            estado="ACTIVO",
            idTaller=nuevo_taller.cod,
            id_rol=rol.id if rol else None
        )
        db.add(nuevo_admin)
        await db.commit()
        await db.refresh(nuevo_admin)
            
    return TenantSchema(
        cod=nuevo_taller.cod,
        nombre=nuevo_taller.nombre,
        direccion=nuevo_taller.direccion,
        estado=nuevo_taller.estado,
        plan_id=nuevo_taller.plan_id,
        admin_correo=payload.admin_correo
    )

@router.put("/{cod}", response_model=TenantSchema)
async def editar_tenant(
    cod: str,
    payload: TenantUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    """Edita la configuracion de un tenant"""
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
    
    return TenantSchema(
        cod=taller.cod,
        nombre=taller.nombre,
        direccion=taller.direccion,
        estado=taller.estado,
        plan_id=taller.plan_id
    )

@router.patch("/{cod}/status", response_model=TenantSchema)
async def cambiar_estado_tenant(
    cod: str,
    payload: TenantStatusUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    """Suspende, Reactiva o Cancela un tenant"""
    taller = await Taller.get_by_cod(db, cod)
    if not taller:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")

    if payload.estado not in ["ACTIVO", "SUSPENDIDO", "CANCELADO"]:
        raise HTTPException(status_code=400, detail="Estado invalido")

    taller.estado = payload.estado
    await db.commit()
    await db.refresh(taller)
    
    return TenantSchema(
        cod=taller.cod,
        nombre=taller.nombre,
        direccion=taller.direccion,
        estado=taller.estado,
        plan_id=taller.plan_id
    )
