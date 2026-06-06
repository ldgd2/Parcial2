import asyncio
import bcrypt
import random
import string
import questionary
from faker import Faker
from rich.console import Console

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal

# Imports de modelos
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.usuario import Usuario
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.cliente import Cliente
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.vehiculo import Vehiculo
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.tecnico import Tecnico
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.sucursal import Sucursal
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.emergencia import Emergencia
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.calificacion import Calificacion
from app.packages.gestion_administrativa_reportes.modules.pagos.models.pago import Pago
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.suscripcion import PlanSuscripcion
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.permisos import Rol

console = Console()
fake = Faker('es_ES')

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def generate_workshop_code() -> str:
    return "T-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

def generate_plate() -> str:
    return ''.join(random.choices(string.ascii_uppercase, k=3)) + "-" + ''.join(random.choices(string.digits, k=3))

from app.db.base import Estado, Prioridad, CategoriaProblema

async def run_procedural_seeder():
    console.print("\n[bold cyan]=== GENERADOR PROCEDURAL AUTOMÁTICO (FAKER) ===[/bold cyan]")
    
    try:
        num_clientes = int(await questionary.text("¿Cuántos clientes (y vehículos) crear?:", default="10").ask_async())
        num_talleres = int(await questionary.text("¿Cuántos talleres crear?:", default="3").ask_async())
        num_tecnicos = int(await questionary.text("¿Cuántos técnicos POR TALLER crear?:", default="2").ask_async())
        num_emergencias = int(await questionary.text("¿Cuántas emergencias e historial (Calificaciones, Pagos) crear?:", default="20").ask_async())
    except ValueError:
        console.print("[bold red]Entrada inválida. Operación cancelada.[/bold red]")
        return

    async with AsyncSessionLocal() as db:
        console.print("\n[bold yellow]Sincronizando datos maestros (Estados, Prioridades, Categorías)...[/bold yellow]")
        
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
        for est_data in estados_data:
            result = await db.execute(select(Estado).filter_by(nombre=est_data["nombre"]))
            if not result.scalars().first():
                db.add(Estado(**est_data))
                
        # 2. CREAR PRIORIDADES
        prioridades_data = [
            {"descripcion": "Baja prioridad"},
            {"descripcion": "Prioridad media"},
            {"descripcion": "Prioridad alta"},
            {"descripcion": "Crítica - Inmediata"},
        ]
        for pri_data in prioridades_data:
            result = await db.execute(select(Prioridad).filter_by(descripcion=pri_data["descripcion"]))
            if not result.scalars().first():
                db.add(Prioridad(**pri_data))
                
        # 3. CREAR CATEGORÍAS
        categorias_data = [
            {"descripcion": "Falla en el motor"},
            {"descripcion": "Problemas eléctricos"},
            {"descripcion": "Neumático pinchado"},
            {"descripcion": "Problemas en frenos"},
            {"descripcion": "A/C no funciona"},
            {"descripcion": "Daño en carrocería"},
            {"descripcion": "Batería descargada"},
        ]
        for cat_data in categorias_data:
            result = await db.execute(select(CategoriaProblema).filter_by(descripcion=cat_data["descripcion"]))
            if not result.scalars().first():
                db.add(CategoriaProblema(**cat_data))
                
        await db.commit()
        
        # 1. Traer Planes (necesario para talleres)
        planes = (await db.execute(select(PlanSuscripcion))).scalars().all()
        if not planes:
            console.print("[bold red]No hay planes de suscripción. Ejecuta primero la opción 1 del Wizard.[/bold red]")
            return
            
        console.print("\n[bold yellow]Generando Clientes y Vehículos...[/bold yellow]")
        clientes_db = []
        vehiculos_db = []
        for _ in range(num_clientes):
            c = Cliente(
                nombre=f"{fake.first_name()} {fake.last_name()}",
                correo=fake.unique.email(),
                contrasena=hash_password("123456")
            )
            db.add(c)
            clientes_db.append(c)
        await db.commit() # Commit to get IDs
        
        for c in clientes_db:
            v = Vehiculo(
                placa=generate_plate(),
                marca=fake.random_element(elements=('Toyota', 'Nissan', 'Hyundai', 'Kia', 'Chevrolet')),
                modelo=fake.word().capitalize(),
                anio=random.randint(2010, 2024),
                idCliente=c.id
            )
            db.add(v)
            vehiculos_db.append(v)
        await db.commit()
        
        console.print(f"[bold green]✓ {num_clientes} Clientes y Vehículos creados.[/bold green]")

        console.print("\n[bold yellow]Generando Talleres y sus Administradores...[/bold yellow]")
        talleres_db = []
        
        # Necesitamos el rol ADMIN_TALLER
        rol_admin_taller = (await db.execute(select(Rol).where(Rol.nombre == "ADMIN_TALLER"))).scalars().first()
        
        for _ in range(num_talleres):
            plan_id = random.choice(planes).id
            t_cod = generate_workshop_code()
            
            # Insert Taller without admin first to satisfy FK constraint from Usuario
            t = Taller(
                cod=t_cod,
                nombre=fake.company(),
                direccion=fake.address(),
                estado="ACTIVO",
                plan_id=plan_id,
            )
            db.add(t)
            await db.commit()
            
            # Crear admin
            admin_email = fake.unique.email()
            admin = Usuario(
                nombre=fake.first_name(),
                apellido=fake.last_name(),
                correo=admin_email,
                contrasena=hash_password("123456"),
                id_rol=rol_admin_taller.id if rol_admin_taller else None,
                estado="ACTIVO",
                idTaller=t_cod
            )
            db.add(admin)
            await db.commit() # Para obtener admin.id
            
            # Actualizar Taller con el admin
            t.id_admin = admin.id
            await db.commit()
            talleres_db.append(t)
            
            # Crear schema de tenant
            from app.core.tenant_utils import get_tenant_schema_name
            from sqlalchemy import text
            schema_name = get_tenant_schema_name(t.nombre, t.cod)
            try:
                await db.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
            except Exception as e:
                console.print(f"[bold red]Error creando schema {schema_name}: {e}[/bold red]")
            
            console.print(f"  - Taller: {t.nombre} | Admin: {admin_email}")
            
        await db.commit()
        
        # Crear Sucursales
        for t in talleres_db:
            s = Sucursal(
                id_taller=t.cod,
                nombre=f"Matriz {t.nombre}",
                direccion=t.direccion,
                estado="ACTIVO"
            )
            db.add(s)
        await db.commit()
        console.print(f"[bold green]✓ {num_talleres} Talleres creados.[/bold green]")

        console.print("\n[bold yellow]Generando Técnicos...[/bold yellow]")
        
        talleres_all = (await db.execute(select(Taller).where(Taller.cod != "ROOT"))).scalars().all()
        
        tecnicos_creados = 0
        for t in talleres_all:
            for _ in range(num_tecnicos):
                tec = Tecnico(
                    nombre=f"{fake.first_name()} {fake.last_name()}",
                    correo=fake.unique.email(),
                    contrasena=hash_password("123456"),
                    telefono=fake.phone_number()[:20],
                    idTaller=t.cod,
                    estado="ACTIVO"
                )
                db.add(tec)
                tecnicos_creados += 1
        await db.commit()
        console.print(f"[bold green]✓ {tecnicos_creados} Técnicos creados.[/bold green]")

        console.print("\n[bold yellow]Generando Emergencias, Pagos y Calificaciones...[/bold yellow]")
        # Refresh vehiculos y talleres
        vehiculos_db = (await db.execute(select(Vehiculo))).scalars().all()
        
        if not vehiculos_db or not talleres_all:
            console.print("[bold red]No hay suficientes datos para generar emergencias.[/bold red]")
            return
            
        emergencias_creadas = 0
        for _ in range(num_emergencias):
            vehiculo = random.choice(vehiculos_db)
            taller = random.choice(talleres_all)
            
            estado = random.choice([1, 2, 3, 4, 5]) # Asumiendo 5=Completada
            
            e = Emergencia(
                descripcion=fake.sentence(nb_words=6),
                direccion=fake.address(),
                latitud=random.uniform(-12.1, -11.9),
                longitud=random.uniform(-77.1, -76.9),
                idTaller=taller.cod,
                idPrioridad=random.choice([1, 2, 3]),
                idCategoria=random.choice([1, 2, 3, 4, 5]),
                idCliente=vehiculo.idCliente,
                placaVehiculo=vehiculo.placa,
                idEstado=estado,
                hora=fake.time_object(),
                es_valida=True
            )
            db.add(e)
            await db.commit()
            
            # Si completada, agregar Pago y Calificacion
            if estado == 5:
                # Pago
                p = Pago(
                    emergencia_id=e.id,
                    cliente_id=vehiculo.idCliente,
                    monto=round(random.uniform(50.0, 500.0), 2),
                    monto_comision=round(random.uniform(5.0, 50.0), 2),
                    metodo_pago_id=str(random.choice([1, 2, 3])),
                    estado="COMPLETADO"
                )
                db.add(p)
                
                # Calificacion
                calif = Calificacion(
                    id_emergencia=e.id,
                    puntuacion=random.randint(3, 5), # Mayormente buenas
                    comentario=fake.sentence(nb_words=10)
                )
                db.add(calif)
                
            emergencias_creadas += 1
            
        await db.commit()
        console.print(f"[bold green]✓ {emergencias_creadas} Emergencias creadas exitosamente.[/bold green]")

if __name__ == "__main__":
    asyncio.run(run_procedural_seeder())
