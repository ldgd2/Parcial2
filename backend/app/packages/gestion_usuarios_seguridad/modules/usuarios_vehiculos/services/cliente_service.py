"""
Servicio de Clientes — CU03
Registro de usuario y vehículo en una sola transacción.
"""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.cliente import Cliente
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.vehiculo import Vehiculo
from app.core.security import hash_password
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.schemas.cliente import ClienteCreate, ClienteOut, ClienteSimpleCreate
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.schemas.vehiculo import VehiculoCreate

async def registrar_cliente_solo(data: ClienteSimpleCreate, db: AsyncSession) -> ClienteOut:
    
    if await Cliente.get_by_correo(db, data.correo):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo electrónico ya está registrado.",
        )
        
    data.contrasena = hash_password(data.contrasena)
    cliente = await Cliente.create(db, obj_in=data)

    return ClienteOut(
        id=cliente.id,
        nombre=cliente.nombre,
        correo=cliente.correo,
        vehiculos=[],
    )

async def registrar_cliente(data: ClienteCreate, db: AsyncSession) -> ClienteOut:
    cliente_simple = ClienteSimpleCreate(
        nombre=data.nombre,
        correo=data.correo,
        contrasena=data.contrasena
    )
    cliente_out = await registrar_cliente_solo(cliente_simple, db)
    nuevo_vehiculo_data = {
        "placa": data.vehiculo.placa,
        "marca": data.vehiculo.marca,
        "modelo": data.vehiculo.modelo,
        "anio": data.vehiculo.anio,
        "idCliente": cliente_out.id
    }
    vehiculo = await Vehiculo.create(db, obj_in=nuevo_vehiculo_data)

    cliente_out.vehiculos = [vehiculo]
    return cliente_out


async def registrar_vehiculo_extra(cliente_id: int, data: VehiculoCreate, db: AsyncSession):
    if await Vehiculo.get_by_placa(db, data.placa):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La placa de vehículo ya se encuentra registrada en el sistema."
        )

    nuevo_vehiculo_data = data.model_dump()
    nuevo_vehiculo_data["idCliente"] = cliente_id
    nuevo_vehiculo = await Vehiculo.create(db, obj_in=nuevo_vehiculo_data)
    
    return nuevo_vehiculo


async def obtener_todos_los_clientes(db: AsyncSession):
    return await Cliente.get_all(db, )


async def obtener_vehiculos_cliente(cliente_id: int, db: AsyncSession):
    return await Vehiculo.get_by_cliente_id(db, cliente_id)
