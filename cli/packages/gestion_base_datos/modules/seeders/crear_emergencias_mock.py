import asyncio
import os
import sys
import random
from datetime import datetime

# Setup paths
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'backend'))
if backend_path not in sys.path:
    sys.path.append(backend_path)

from app.db.session import AsyncSessionLocal, engine
from app.db.base import Base
from sqlalchemy import select

from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.cliente import Cliente
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.vehiculo import Vehiculo
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.emergencia import Emergencia
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.estado import Estado
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.categoria_problema import CategoriaProblema
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.prioridad import Prioridad
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.historial_estado import HistorialEstado
from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.models.resumen_ia import ResumenIA
from app.core.security import hash_password

# Coordenadas proporcionadas por el usuario en Santa Cruz
COORDENADAS = [
    (-17.814942, -63.206901),
    (-17.826528, -63.198833),
    (-17.787909, -63.185986),
    (-17.807563, -63.169530),
    (-17.826666, -63.221352),
]

DESCRIPCIONES = [
    ("Falla de Frenos", "Los frenos no responden y hacen un ruido metálico fuerte.", "Av. Cristo Redentor y 4to Anillo"),
    ("Motor Sobrecalentado", "Sale mucho humo blanco del capó y la aguja de temperatura está al máximo.", "Av. Banzer Km 5"),
    ("Batería Muerta", "El auto no enciende, hace un clic, creo que dejé las luces prendidas toda la noche.", "Doble Vía a La Guardia Km 6"),
    ("Pinchazo Múltiple", "Caí en un bache gigante y reventé dos llantas, no tengo repuesto doble.", "Av. Santos Dumont 5to Anillo"),
    ("Transmisión Trabada", "La palanca de cambios se trabó en segunda y huele a embrague quemado.", "Radial 17 y medio"),
]

MOCK_IA = [
    {
        "resumen": "Falla inminente en el sistema de frenado. Requiere grúa.",
        "ficha": {"diagnostico_probable": "Desgaste total de balatas o pérdida de líquido de frenos", "posibles_causas": ["Mantenimiento deficiente"], "piezas_necesarias": ["Balatas", "Líquido de frenos"], "protocolo_tecnico": ["Revisión de discos y mordazas"]}
    },
    {
        "resumen": "Sobrecalentamiento severo del motor. Riesgo de fundición.",
        "ficha": {"diagnostico_probable": "Fuga de refrigerante o falla en termostato/electroventilador", "posibles_causas": ["Manguera rota", "Termostato pegado"], "piezas_necesarias": ["Refrigerante", "Mangueras"], "protocolo_tecnico": ["Prueba de presión del sistema"]}
    },
    {
        "resumen": "Falla eléctrica primaria. Batería o alternador.",
        "ficha": {"diagnostico_probable": "Batería descargada o alternador defectuoso", "posibles_causas": ["Luces encendidas", "Fin de vida útil de batería"], "piezas_necesarias": ["Batería nueva"], "protocolo_tecnico": ["Prueba con multímetro"]}
    },
    {
        "resumen": "Daño estructural en neumáticos y posiblemente aros.",
        "ficha": {"diagnostico_probable": "Reventón por impacto contundente", "posibles_causas": ["Bache profundo"], "piezas_necesarias": ["Neumáticos nuevos", "Aros (posible)"], "protocolo_tecnico": ["Balanceo y alineación obligatoria"]}
    },
    {
        "resumen": "Daño en el sistema de embrague/transmisión.",
        "ficha": {"diagnostico_probable": "Disco de embrague quemado o horquilla trabada", "posibles_causas": ["Desgaste severo", "Sobrecalentamiento por mal uso"], "piezas_necesarias": ["Kit de embrague"], "protocolo_tecnico": ["Desmontaje de caja de cambios"]}
    }
]

def generate_plate():
    letters = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
    numbers = "".join(random.choices("0123456789", k=3))
    return f"{letters}-{numbers}"

from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.tecnico import Tecnico
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.especialidad import Especialidad
from app.packages.gestion_emergencias_solicitudes.modules.auxilio_solicitudes.models.asignacion_especialidad import AsignacionEspecialidad

async def seed_emergencias_mock():
    print("\n--- INICIANDO CREACIÓN DE EMERGENCIAS MOCK (SANTA CRUZ) ---")
    async with AsyncSessionLocal() as db:
        # Obtener IDs base
        est_pend = (await db.execute(select(Estado.id).where(Estado.nombre == "PENDIENTE"))).scalar_one_or_none()
        cat_mecanica = (await db.execute(select(CategoriaProblema.id))).scalars().first()
        prio_alta = (await db.execute(select(Prioridad.id))).scalars().first()
        
        if not est_pend or not cat_mecanica or not prio_alta:
            print("[ERROR] Faltan datos base en la BD (Estados, Categorías o Prioridades). Ejecuta el Seeder primero.")
            return

        # ==========================================
        # 1. CREAR O VERIFICAR TALLER MOCK Y TENANT
        # ==========================================
        taller_mock = (await db.execute(select(Taller).where(Taller.cod == "TAL-MOCK"))).scalar_one_or_none()
        
        if not taller_mock:
            print(">> Creando Taller Mock (Santa Cruz) para que puedas probar el dashboard...")
            taller_mock = Taller(cod="TAL-MOCK", nombre="Taller Santa Cruz", direccion="Av. San Martin", estado="ACTIVO", latitud=-17.7833, longitud=-63.1821)
            db.add(taller_mock)
            await db.flush()
            
            # Asignar TODAS las especialidades al taller mock para que reciba cualquier emergencia
            especialidades = (await db.execute(select(Especialidad))).scalars().all()
            for esp in especialidades:
                db.add(AsignacionEspecialidad(idTaller=taller_mock.cod, idEspecialidad=esp.id))
        else:
            print(">> Taller Mock (TAL-MOCK) ya existe. Usándolo...")

        # Crear o verificar un técnico para loguearse (App Móvil)
        tecnico_mock = (await db.execute(select(Tecnico).where(Tecnico.correo == "tecnico.mock@email.com"))).scalar_one_or_none()
        if not tecnico_mock:
            tecnico_mock = Tecnico(
                nombre="Roberto (Técnico Mock)",
                correo="tecnico.mock@email.com",
                contrasena=hash_password("admin123"),
                telefono="77788899",
                idTaller=taller_mock.cod
            )
            db.add(tecnico_mock)
            await db.flush()
            
        # Crear o verificar un Admin para loguearse (Dashboard Web)
        from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.usuario import Usuario
        admin_mock = (await db.execute(select(Usuario).where(Usuario.correo == "admin.mock@email.com"))).scalar_one_or_none()
        if not admin_mock:
            admin_mock = Usuario(
                nombre="Admin Mock",
                apellido="Santa Cruz",
                correo="admin.mock@email.com",
                contrasena=hash_password("admin123"),
                estado="ACTIVO",
                idTaller=taller_mock.cod
            )
            db.add(admin_mock)
            await db.flush()
            
        print("   ✅ Taller Activo: TAL-MOCK")
        print("   🔑 LOGIN DASHBOARD WEB (Administrador): admin.mock@email.com / admin123")
        print("   📱 LOGIN APP MÓVIL (Técnico): tecnico.mock@email.com / admin123")

        # ==========================================
        # 2. CREAR VEHÍCULOS Y CLIENTES
        # ==========================================
        res_v = await db.execute(select(Vehiculo))
        vehiculos = res_v.scalars().all()
        
        while len(vehiculos) < 5:
            c = Cliente(nombre=f"Cliente Mock {len(vehiculos)+1}", correo=f"mock{len(vehiculos)+1}@email.com", contrasena=hash_password("123456"))
            db.add(c)
            await db.flush()
            v = Vehiculo(placa=generate_plate(), marca="Toyota", modelo="Corolla", anio=2020, idCliente=c.id)
            db.add(v)
            await db.flush()
            vehiculos.append(v)
            
        await db.commit()
        
        # Obtener IDs base
        est_pend = (await db.execute(select(Estado.id).where(Estado.nombre == "PENDIENTE"))).scalar_one_or_none()
        cat_mecanica = (await db.execute(select(CategoriaProblema.id))).scalars().first()
        prio_alta = (await db.execute(select(Prioridad.id))).scalars().first()
        
        if not est_pend or not cat_mecanica or not prio_alta:
            print("[ERROR] Faltan datos base en la BD (Estados, Categorías o Prioridades). Ejecuta el Seeder primero.")
            return

        print("Insertando 5 emergencias geolocalizadas en Santa Cruz con datos pre-mapeados...")
        
        for i in range(5):
            vehiculo = vehiculos[i % len(vehiculos)]
            coord = COORDENADAS[i]
            desc = DESCRIPCIONES[i]
            mock_ia = MOCK_IA[i]
            
            # Crear emergencia
            e = Emergencia(
                descripcion=desc[0],
                texto_adicional=desc[1],
                direccion=desc[2],
                latitud=coord[0],
                longitud=coord[1],
                hora=datetime.now().time(),
                idTaller=None, # Taller debe descubrirlo
                idPrioridad=prio_alta,
                idCategoria=cat_mecanica,
                idCliente=vehiculo.idCliente,
                placaVehiculo=vehiculo.placa
            )
            db.add(e)
            await db.flush()
            
            # Historial estado PENDIENTE
            db.add(HistorialEstado(idEmergencia=e.id, idEstado=est_pend))
            
            # Resumen IA mockeado
            db.add(ResumenIA(
                resumen=mock_ia["resumen"],
                ficha_tecnica=mock_ia["ficha"],
                idEmergencia=e.id
            ))
            
            print(f"✅ Emergencia Creada: '{desc[0]}' en {desc[2]} ({coord[0]}, {coord[1]})")
            
        await db.commit()
        print("\n🎉 ¡Listas para ser vistas en los Talleres!")

if __name__ == "__main__":
    if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_emergencias_mock())
