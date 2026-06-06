import sys
import os
from pathlib import Path
import bcrypt
import asyncio

# Agregar backend al path - método más robusto
current_dir = Path(__file__).resolve().parent
backend_path = current_dir.parent.parent.parent.parent.parent / "backend"
backend_str = str(backend_path.absolute())

if backend_str not in sys.path:
    sys.path.insert(0, backend_str)

print(f"Backend path: {backend_str}")
print(f"Sys.path[0]: {sys.path[0]}")

try:
    from app.db.session import AsyncSessionLocal
    from app.db.base import (
        Estado, Prioridad, Especialidad, CategoriaProblema, Taller, Tecnico,
        TecnicoEspecialidad, Cliente, Vehiculo
    )
    from sqlalchemy import select
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print(f"Backend path: {backend_str}")
    print(f"Contenidos: {list(Path(backend_str).iterdir())[:5]}")
    sys.exit(1)


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


async def seed_database():
    db = AsyncSessionLocal()
    try:
        print("\n🌱 Iniciando seed de base de datos...\n")

        # 1. CREAR ESTADOS
        estados_data = [
            {"nombre": "REPORTADO", "descripcion": "Emergencia reportada"},
            {"nombre": "ASIGNADO", "descripcion": "Técnico asignado"},
            {"nombre": "EN_RUTA", "descripcion": "Técnico en ruta"},
            {"nombre": "ATENDIENDO", "descripcion": "Atendiendo emergencia"},
            {"nombre": "FINALIZADO", "descripcion": "Emergencia finalizada"},
            {"nombre": "CANCELADO", "descripcion": "Emergencia cancelada"},
            {"nombre": "PAGADO", "descripcion": "Emergencia pagada"},
        ]
        estados = []
        for est_data in estados_data:
            result = await db.execute(select(Estado).filter_by(nombre=est_data["nombre"]))
            estado = result.scalars().first()
            if not estado:
                estado = Estado(**est_data)
                db.add(estado)
            estados.append(estado)
        await db.commit()
        print(f"✅ {len(estados)} estados creados")

        # 2. CREAR PRIORIDADES
        prioridades_data = [
            {"descripcion": "Baja prioridad"},
            {"descripcion": "Prioridad media"},
            {"descripcion": "Prioridad alta"},
            {"descripcion": "Crítica - Inmediata"},
        ]
        prioridades = []
        for pri_data in prioridades_data:
            result = await db.execute(select(Prioridad).filter_by(descripcion=pri_data["descripcion"]))
            prioridad = result.scalars().first()
            if not prioridad:
                prioridad = Prioridad(**pri_data)
                db.add(prioridad)
            prioridades.append(prioridad)
        await db.commit()
        print(f"✅ {len(prioridades)} prioridades creadas")

        # 3. CREAR ESPECIALIDADES
        especialidades_data = [
            {"nombre": "Mecánica General", "descripcion": "Reparaciones mecánicas"},
            {"nombre": "Electricidad", "descripcion": "Sistema eléctrico"},
            {"nombre": "Neumáticos", "descripcion": "Cambio y reparación de llantas"},
            {"nombre": "Frenos", "descripcion": "Sistema de frenos"},
            {"nombre": "Aire Acondicionado", "descripcion": "Sistema A/C"},
            {"nombre": "Pintura", "descripcion": "Trabajos de pintura"},
        ]
        especialidades = []
        for esp_data in especialidades_data:
            result = await db.execute(select(Especialidad).filter_by(nombre=esp_data["nombre"]))
            especialidad = result.scalars().first()
            if not especialidad:
                especialidad = Especialidad(**esp_data)
                db.add(especialidad)
            especialidades.append(especialidad)
        await db.commit()
        print(f"✅ {len(especialidades)} especialidades creadas")

        # 4. CREAR CATEGORÍAS DE PROBLEMAS
        categorias_data = [
            {"descripcion": "Falla en el motor"},
            {"descripcion": "Problemas eléctricos"},
            {"descripcion": "Neumático pinchado"},
            {"descripcion": "Problemas en frenos"},
            {"descripcion": "A/C no funciona"},
            {"descripcion": "Daño en carrocería"},
            {"descripcion": "Batería descargada"},
        ]
        categorias = []
        for cat_data in categorias_data:
            result = await db.execute(select(CategoriaProblema).filter_by(descripcion=cat_data["descripcion"]))
            categoria = result.scalars().first()
            if not categoria:
                categoria = CategoriaProblema(**cat_data)
                db.add(categoria)
            categorias.append(categoria)
        await db.commit()
        print(f"✅ {len(categorias)} categorías de problemas creadas")

        # 5. CREAR TALLERES
        talleres_data = [
            {
                "cod": "T001",
                "nombre": "Taller Central La Paz",
                "direccion": "Av. Montes 520",
                "latitud": -17.7833,
                "longitud": -63.1821,
                "estado": "ACTIVO",
            },
            {
                "cod": "T002",
                "nombre": "Taller Express Zona Sur",
                "direccion": "Av. Costanera 1250",
                "latitud": -17.8000,
                "longitud": -63.1900,
                "estado": "ACTIVO",
            },
            {
                "cod": "T003",
                "nombre": "Taller Premium Sopocachi",
                "direccion": "Calle 25, Sopocachi",
                "latitud": -17.7700,
                "longitud": -63.1900,
                "estado": "ACTIVO",
            },
        ]
        talleres = []
        for tal_data in talleres_data:
            result = await db.execute(select(Taller).filter_by(cod=tal_data["cod"]))
            taller = result.scalars().first()
            if not taller:
                taller = Taller(**tal_data)
                db.add(taller)
            talleres.append(taller)
        await db.commit()
        print(f"✅ {len(talleres)} talleres creados")

        # 6. CREAR TÉCNICOS
        tecnicos_data = [
            {
                "nombre": "Juan Pérez",
                "correo": "juan.perez@tallercentral.com",
                "contrasena": hash_password("tecnico123"),
                "telefono": "591-70000001",
                "estado": "DISPONIBLE",
                "idTaller": "T001",
                "especialidades": ["Mecánica General", "Electricidad"],
            },
            {
                "nombre": "Carlos López",
                "correo": "carlos.lopez@tallercentral.com",
                "contrasena": hash_password("tecnico123"),
                "telefono": "591-70000002",
                "estado": "DISPONIBLE",
                "idTaller": "T002",
                "especialidades": ["Neumáticos", "Frenos"],
            },
            {
                "nombre": "Roberto Silva",
                "correo": "roberto.silva@express.com",
                "contrasena": hash_password("tecnico123"),
                "telefono": "591-70000003",
                "estado": "DISPONIBLE",
                "idTaller": "T003",
                "especialidades": ["Aire Acondicionado", "Pintura"],
            },
            {
                "nombre": "Miguel Ángel Rojas",
                "correo": "miguel.rojas@premium.com",
                "contrasena": hash_password("tecnico123"),
                "telefono": "591-70000004",
                "estado": "DISPONIBLE",
                "idTaller": "T001",
                "especialidades": ["Mecánica General", "Electricidad", "Neumáticos"],
            },
            {
                "nombre": "Fernando Torres",
                "correo": "fernando.torres@tallercentral.com",
                "contrasena": hash_password("tecnico123"),
                "telefono": "591-70000005",
                "estado": "EN_RUTA",
                "idTaller": "T002",
                "especialidades": ["Frenos", "Aire Acondicionado"],
            },
        ]

        tecnicos = []
        for tec_data in tecnicos_data:
            especialidades_nombres = tec_data.pop("especialidades")
            result = await db.execute(select(Tecnico).filter_by(correo=tec_data["correo"]))
            tecnico = result.scalars().first()
            if not tecnico:
                tecnico = Tecnico(**tec_data)
                db.add(tecnico)
                await db.flush()
                # Asignar especialidades
                for esp_nombre in especialidades_nombres:
                    result_esp = await db.execute(select(Especialidad).filter_by(nombre=esp_nombre))
                    especialidad = result_esp.scalars().first()
                    if especialidad:
                        tech_esp = TecnicoEspecialidad(idTecnico=tecnico.id, idEspecialidad=especialidad.id)
                        db.add(tech_esp)
            tecnicos.append(tecnico)
        await db.commit()
        print(f"✅ {len(tecnicos)} técnicos creados")

        # 7. CREAR CLIENTES
        clientes_data = [
            {
                "nombre": "Ana María",
                "correo": "ana.maria@email.com",
                "contrasena": hash_password("cliente123"),
            },
            {
                "nombre": "Roberto Fernández",
                "correo": "roberto.f@email.com",
                "contrasena": hash_password("cliente123"),
            },
            {
                "nombre": "María García",
                "correo": "maria.garcia@email.com",
                "contrasena": hash_password("cliente123"),
            },
            {
                "nombre": "Pedro López",
                "correo": "pedro.lopez@email.com",
                "contrasena": hash_password("cliente123"),
            },
            {
                "nombre": "Juanita Ramírez",
                "correo": "juanita.r@email.com",
                "contrasena": hash_password("cliente123"),
            },
        ]
        clientes = []
        for cli_data in clientes_data:
            result = await db.execute(select(Cliente).filter_by(correo=cli_data["correo"]))
            cliente = result.scalars().first()
            if not cliente:
                cliente = Cliente(**cli_data)
                db.add(cliente)
            clientes.append(cliente)
        await db.commit()
        print(f"✅ {len(clientes)} clientes creados")

        # 8. CREAR VEHÍCULOS
        vehiculos_data = [
            {"placa": "ABC-123", "marca": "Toyota", "modelo": "Corolla", "anio": 2020, "idCliente": clientes[0].id},
            {"placa": "DEF-456", "marca": "Honda", "modelo": "Civic", "anio": 2019, "idCliente": clientes[0].id},
            {"placa": "GHI-789", "marca": "Nissan", "modelo": "Altima", "anio": 2021, "idCliente": clientes[1].id},
            {"placa": "JKL-012", "marca": "Ford", "modelo": "Focus", "anio": 2018, "idCliente": clientes[1].id},
            {"placa": "MNO-345", "marca": "Chevrolet", "modelo": "Cruze", "anio": 2022, "idCliente": clientes[2].id},
            {"placa": "PQR-678", "marca": "Hyundai", "modelo": "Elantra", "anio": 2020, "idCliente": clientes[2].id},
            {"placa": "STU-901", "marca": "Kia", "modelo": "Optima", "anio": 2019, "idCliente": clientes[3].id},
            {"placa": "VWX-234", "marca": "Mazda", "modelo": "3", "anio": 2021, "idCliente": clientes[3].id},
        ]
        vehiculos = []
        for veh_data in vehiculos_data:
            result = await db.execute(select(Vehiculo).filter_by(placa=veh_data["placa"]))
            vehiculo = result.scalars().first()
            if not vehiculo:
                vehiculo = Vehiculo(**veh_data)
                db.add(vehiculo)
            vehiculos.append(vehiculo)
        await db.commit()
        print(f"✅ {len(vehiculos)} vehículos creados")

        print("\n✅ SEED COMPLETADO EXITOSAMENTE\n")
        print("📋 Credenciales de acceso:")
        print("\n👨‍🔧 Técnicos:")
        for tec in tecnicos_data:
            print(f"  {tec['correo']} / tecnico123")
        print("\n👥 Clientes:")
        for cli in clientes_data:
            print(f"  {cli['correo']} / cliente123")
        print("\n💡 Las emergencias se crean consumiendo la API desde la interfaz o móvil.")

    except Exception as e:
        await db.rollback()
        print(f"\n❌ Error durante el seed: {e}\n")
        raise
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(seed_database())
