import asyncio
import platform
import warnings
import os
import sys
import random
from datetime import datetime, timedelta
from sqlalchemy import text, select, func
from faker import Faker

# Setup paths
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
if backend_path not in sys.path:
    sys.path.append(backend_path)

from app.db.session import AsyncSessionLocal, engine
from app.db.base import Base
from app.core.security import hash_password
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.cliente import Cliente
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.vehiculo import Vehiculo
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.tecnico import Tecnico
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.emergencia import Emergencia
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.estado import Estado
from app.packages.gestion_administrativa_reportes.modules.pagos.models.pago import Pago
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.historial_estado import HistorialEstado
from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.models.resumen_ia import ResumenIA
from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.services.ai_service import analizar_transcripcion_whisper

# Silenciar el aviso de deprecación de loop policy en Python 3.14+
warnings.filterwarnings("ignore", category=DeprecationWarning)

fake = Faker('es_MX')

# --- BANCO DE PROMPTS REALISTAS (20+) ---
PROMPTS_EMERGENCIA = [
    "Mi coche se detuvo de la nada en la avenida y sale humo blanco denso del motor. Huele a quemado.",
    "Tengo una llanta ponchada en la carretera y el gato hidráulico no sirve. Estoy con mi familia.",
    "El tablero marca sobrecalentamiento y se apagó el motor. Estoy en medio del tráfico.",
    "Escucho un ruido metálico horrible al frenar y el pedal se siente muy esponjoso.",
    "Choqué por alcance, el radiador está goteando líquido verde y no puedo cerrar el capó.",
    "Iba a 120 km/h, pisé un bache y mi carro hizo noclip. Creo que caí en los Backrooms, huele a alfombra húmeda y hay luces fluorescentes amarillas. ¿La grúa llega hasta acá?",
    "Le eché dos latas de Monster Energy al tanque porque me quedé sin gasolina y ahora mi Honda Civic está levitando a medio metro del piso vibrando violentamente.",
    "Intenté descargarle más RAM a la computadora del auto por WiFi y ahora los controles están invertidos. Si giro a la derecha, voy a la izquierda. Si freno, toca el claxon.",
    "El carro hizo un sonido de *Vine Boom* fuertísimo, el motor se apagó de golpe y ahora la pantalla del estéreo solo dice 'YOU DIED' en letras rojas.",
    "Mi mecánico me dijo que el motor está 'cooked'. Le pregunté qué pieza específica falló y me respondió 'it's over bro, gg'. El auto está en llamas frente a mí.",
    "Toqué un botón del tablero que nunca había visto, el parabrisas tomó una captura de pantalla con flash y ahora el coche lleva 40 minutos en una pantalla de carga.",
    "El GPS me dijo que girara a la derecha en medio de un bosque, lo hice, el cielo se puso rojo y apareció una barra de vida de un jefe en el cielo. Mi auto no quiere retroceder.",
    "El testigo de check engine llevaba prendido 4 años. Hoy el motor literalmente escupió un pistón por el capó, rompió el parabrisas y hay un agujero donde estaba el bloque.",
    "Venía escuchando phonk a todo volumen, me creí de Tokyo Drift en una rotonda mojada y ahora mi coche está abrazando íntimamente un poste de luz. El poste ganó.",
    "Le puse un alerón gigante de plástico y luces neón de AliExpress. La batería hizo un chispazo, se derritió la caja de fusibles y estoy atrapado adentro porque los seguros son eléctricos.",
    "Me quedé dormido, me salí de la ruta y desperté en un pantano. El agua me llega a las ventanas y creo que el tronco que está al lado de mi puerta me acaba de parpadear.",
    "La rueda delantera izquierda decidió independizarse. Vi cómo me rebasaba rodando sola mientras yo sacaba chispas con el disco de freno contra el asfalto. Mándenme ayuda.",
    "El coeficiente de arrastre aerodinámico colapsó tras perder el splitter frontal de fibra de carbono. El downforce es nulo y la ECU cortó la inyección por seguridad activa.",
    "Hay una discrepancia milimétrica en el camber negativo de la suspensión roscada, lo que arruinó por completo mi apex en la última horquilla. Requiero asistencia en plataforma flatbed, no un simio con cadenas.",
    "La telemetría en tiempo real de mi Stage 3 indica una despresurización catastrófica en los turbos gemelos. El log marca que estoy corriendo peligrosamente pobre de mezcla. Ni se te ocurra mandar una grúa de arrastre.",
    "El carro se siente... deprimido. Como que acelero pero no tiene ganas de vivir.",
    "Huele a matemáticas en la cabina. No sé cómo explicarlo, como a circuitos sobrecalentados o a tarea quemada, y me pican los ojos.",
    "Cada vez que paso de 60 km/h escucho a alguien susurrar en la parte de atrás, pero vengo solo. Ah, y el volante vibra poquito.",
    "El auto hace un ruido de 'clac-clac-clac' pero solo cuando es de noche y hace frío, si hay sol funciona perfecto.",
    "Caí en un bache en el Edomex que literalmente tiene su propio ecosistema y código postal. Mi rin izquierdo dejó de existir en este plano astral y unos güeyes en una Italika sin placas ya pasaron tres veces mirándome feo.",
    "Se me sobrecalentó el Chevy a media carretera libre. Intenté abrir el cofre, me quemé las manos, y para rematar un trailero me aventó un vaso con orines que me cayó en el parabrisas. Manda grúa y cloro.",
    "El pendejo de mi primo me dijo que le pusiera thinner al tanque porque rinde más que la Magna. Ahora mi Tsuru suena como lavadora con tenis adentro, huele a mona de guayaba y el cofre salió volando.",
    "Choqué contra un carrito de tamales porque venía farmeando moneditas en TapSwap. Mi motor está bañado en atole hirviendo, el radiador gotea champurrado y el tamalero está sacando un machete. Manda al MP o una ambulancia.",
    "Me quedé tirado y la única grúa que se paró a 'ayudarme' tiene un sticker de la Santa Muerte, huele a foco quemado y el chofer me acaba de preguntar mi tipo de sangre. Cancela todo, mejor le rezo a Dios.",
    "El motor se apagó de la nada justo cuando le estaba explicando a mi compa que Epstein no se suicidó. Ahora mi estéreo solo reproduce números en ruso y hay una Ford Lobo blanca sin placas espejeándome. Ayuda rápida.",
    "El tablero marca que necesito cambiar el líquido de direccionales, pero creo que la junta de la trócola hizo mitosis. El clutch me está insultando en arameo y el asiento del copiloto huele a azufre.",
    "Toqué la bocina para mentarle la madre a un microbusero y por algún motivo el volante me dio una descarga eléctrica que me reinició el sistema nervioso. Estoy viendo fractales y mi carro está haciendo T-pose en la banqueta.",
    "Compré este Jetta en Marketplace a un tal 'El Patrón'. Se le cayó la fascia en un tope y descubrí dos kilos de algo envuelto en cinta canela en la defensa. Me vienen siguiendo dos camionetas blindadas. ¿La asistencia en el camino cubre balaceras?",
    "Iba haciendo mewing a 140 km/h viendo un TikTok de Subway Surfers abajo y un güey cortando arena kinética arriba. Me distraje 0.1 segundos y ahora mi carro es parte estructural de un Oxxo. No rompí mi racha de looksmaxxing pero no siento las piernas.",
    "Le hice caso a un esquizofrénico de r/AutosMexico y le eché aceite de cocina al motor para 'lubricar los metales como los hombres de verdad'. Escupió una biela que le dio a un perro callejero y ahora mi carro es una freidora de papas gigante.",
    "Mi novia me cortó por WhatsApp mientras iba manejando. Quise hacerme el protagonista triste y aceleré con música de The Smiths, pero me estampé contra un camión de basura. Ahora estoy llorando oliendo a pañales cagados. Grúa por favor.",
    "El chasis de mi carro tiene la misma integridad estructural que las rodillas de un mod de Discord. Pasé un tope de plaza comercial y se partió a la mitad como galleta María. El chasis literalmente hizo *crunch*.",
    "El mecánico que me arregló los frenos me cobró en NFTs de changos feos. Ahorita estoy yéndome de pique en una bajada y descubrí que me hizo un 'rug pull' con las balatas. Adiós mundo.",
    "Mi coche se identificó hoy como un peatón y se rehusó a prender. Me mandó un cease and desist por intentar meter la llave. Necesito asistencia legal automotriz o un exorcista de metales.",
    "Iba cruzando un semáforo, el mundo tuvo una caída de frames horrible, mi ping subió a 900 y mi Sentra hizo clip a través del pavimento. Estoy en el nivel 0 de los Backrooms y el radiador está goteando en la alfombra húmeda.",
    "Le instalé un chip de 'potencia' de AliExpress que me costó 4 dólares. Aceleré a fondo, la computadora del carro gritó 'BING CHILLING', se bloquearon las puertas y me está llevando directo a una embajada china. No tengo control del volante.",
    "Mi coche sufre de ansiedad social severa. Había mucho tráfico, se estresó, apagó el motor, subió las ventanas con seguro y puso la alarma para que nadie se acerque. Llevo dos horas aquí encerrado con mi propio sudor.",
    "Venía pisteando bien tranqui, no vi la glorieta y mi carro decidió que era buena idea saltarla estilo Dukes de Hazzard. Aterricé arriba de la estatua de un héroe patrio. El motor está perforado por una espada de bronce y yo perdí mi dignidad."
]

# --- UTILIDADES ---

def generate_plate():
    letters = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
    numbers = "".join(random.choices("0123456789", k=3))
    return f"{letters}-{numbers}"

async def ensure_db_initialized():
    try:
        from init_db import check_and_create_db
        await check_and_create_db()
    except Exception: pass
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# --- FÁBRICAS DE DATOS ---

async def seed_evidencia(db, emergencia_id):
    types = ["foto_frontal.jpg", "foto_motor.jpg", "video_humo.mp4", "foto_tablero.png"]
    for i in range(random.randint(1, 3)):
        ev = Evidencia(
            direccion=f"https://storage.tallernavajasuiza.com/evidencias/E{emergencia_id}_{random.choice(types)}",
            idEmergencia=emergencia_id
        )
        db.add(ev)

async def seed_full_lifecycle(db, emergencia_id):
    # Generar un historial de estados lógico
    estados = (await db.execute(select(Estado))).scalars().all()
    est_map = {e.nombre: e.id for e in estados}
    
    # Flujo: INICIADA -> PENDIENTE -> ENVIADA -> EN_PROCESO -> ATENDIDO (opcional)
    timeline = ["INICIADA", "PENDIENTE", "ENVIADA"]
    if random.random() > 0.4: timeline.append("EN_PROCESO")
    if random.random() > 0.6: timeline.append("ATENDIDO")
    
    start_time = datetime.now() - timedelta(hours=random.randint(1, 24))
    for i, est_name in enumerate(timeline):
        change_time = start_time + timedelta(minutes=i*15 + random.randint(1, 10))
        db.add(HistorialEstado(
            idEmergencia=emergencia_id, 
            idEstado=est_map[est_name],
            fecha_cambio=change_time
        ))
        
    return timeline[-1] # Retorna el estado final alcanzado

async def seed_payment(db, emergencia_id, final_status):
    if final_status == "ATENDIDO":
        monto = random.randint(50, 500)
        p = Pago(monto=monto, monto_comision=monto * 0.1, fecha_pago=datetime.now().date())
        db.add(p)
        await db.flush()
        
        # Vincular usando ORM (evita problemas de nombres de columnas)
        e = await db.get(Emergencia, emergencia_id)
        if e:
            e.idPago = p.id

# --- MOTOR DE IA CONCURRENTE ---

sem = asyncio.Semaphore(5) # Límite de 5 llamadas simultáneas a la IA

async def process_ia_worker(db_context, e, use_real_ia):
    async with sem:
        async with db_context() as db:
            # Re-obtener la emergencia para esta sesión
            emergencia = await db.get(Emergencia, e.id)
            if not emergencia: return

            cats = (await db.execute(select(CategoriaProblema))).scalars().all()
            prios = (await db.execute(select(Prioridad))).scalars().all()
            categorias_map = [{"id": c.id, "nombre": c.descripcion} for c in cats]
            prioridades_map = [{"id": p.id, "nombre": p.descripcion} for p in prios]

            print(f"  [AI-BUSY] Procesando Emergencia #{emergencia.id}...")
            try:
                ia_result = await analizar_transcripcion_whisper(
                    texto_crudo=emergencia.texto_adicional,
                    categorias_disponibles=categorias_map,
                    prioridades_disponibles=prioridades_map
                )
                
                emergencia.idCategoria = ia_result.id_categoria
                emergencia.idPrioridad = ia_result.id_prioridad
                
                resumen = ResumenIA(
                    resumen=ia_result.resumen_taller,
                    ficha_tecnica=ia_result.ficha_tecnica.model_dump(),
                    idEmergencia=emergencia.id
                )
                db.add(resumen)
                
                # Avanzar estado si se analizó con éxito
                est_pend = (await db.execute(select(Estado).where(Estado.nombre == "PENDIENTE"))).scalar_one_or_none()
                if est_pend:
                    db.add(HistorialEstado(idEmergencia=emergencia.id, idEstado=est_pend.id))
                
                await db.commit()
                print(f"  [AI-OK] Emergencia #{emergencia.id} finalizada por IA.")
            except Exception as ex:
                print(f"  [AI-FAIL] Error en #{emergencia.id}: {ex}. Aplicando fallback...")
                # Fallback: Categoría "Otros" (5), Prioridad "Media" (2)
                emergencia.idCategoria = 5
                emergencia.idPrioridad = 2
                
                resumen = ResumenIA(
                    resumen="[FALLBACK] El sistema de IA está saturado. Por favor, analice el audio/texto manualmente.",
                    ficha_tecnica={"causas_probables": ["Desconocido"], "materiales_necesarios": ["Herramientas básicas"]},
                    idEmergencia=emergencia.id
                )
                db.add(resumen)
                
                est_pend = (await db.execute(select(Estado).where(Estado.nombre == "PENDIENTE"))).scalar_one_or_none()
                if est_pend:
                    db.add(HistorialEstado(idEmergencia=emergencia.id, idEstado=est_pend.id))
                
                await db.commit()
                # Pequeña espera para no saturar la API en el siguiente intento
                await asyncio.sleep(1)

# --- ORQUESTADOR ---

async def seed_world_builder(talleres=5, clientes=10, emergencias=5, use_real_ia=True):
    await ensure_db_initialized()
    print(f"\n{'='*20} WORLD BUILDER: POBLADO TOTAL {'='*20}")
    
    async with AsyncSessionLocal() as db:
        from seed import seed as run_base_seed
        await run_base_seed()
        
        # 1. Talleres Ricos
        taller_list = []
        if talleres > 0:
            print(f">> Construyendo {talleres} Talleres con especialistas...")
            for _ in range(talleres):
                cod = f"T{random.randint(1000, 9399)}"
                t = Taller(cod=cod, nombre=f"Taller {fake.company()}", direccion=fake.address(), estado="ACTIVO")
                db.add(t)
                taller_list.append(cod)
                
                # Asignar especialidades al taller (Todas para el demo)
                especialidades = (await db.execute(select(Especialidad))).scalars().all()
                for esp in especialidades:
                    db.add(AsignacionEspecialidad(idTaller=cod, idEspecialidad=esp.id))

                # Técnicos expertos
                for _ in range(random.randint(2, 4)):
                    db.add(Tecnico(
                        nombre=fake.name(), 
                        correo=fake.unique.email(), 
                        contrasena=hash_password("admin123"),
                        telefono=str(random.randint(60000000, 79999999)),
                        idTaller=cod
                    ))
            await db.commit()
        
        # Inteligencia: Si no hay talleres creados, buscar existentes en la BD
        if not taller_list:
            res_t = await db.execute(select(Taller.cod))
            taller_list = [r[0] for r in res_t.all()]
            if taller_list:
                print(f">> Detectados {len(taller_list)} talleres existentes en BD.")
            else:
                # Fallback absoluto (TAL001 del seed base)
                taller_list = ["TAL001"]
                print(">> Usando taller default 'TAL001'.")

        # 2. Clientes y Vehículos
        cliente_ids = []
        vehiculo_placas = []
        if clientes > 0:
            print(f">> Poblando {clientes} Clientes y sus Vehículos...")
            for _ in range(clientes):
                c = Cliente(nombre=fake.name(), correo=fake.unique.email(), contrasena=hash_password("cliente123"))
                db.add(c)
                await db.flush()
                cliente_ids.append(c.id)
                placa = generate_plate()
                v = Vehiculo(placa=placa, marca=random.choice(["Toyota", "Nissan", "Ford", "Chevrolet", "BMW"]), modelo=fake.word().capitalize(), anio=random.randint(2005, 2024), idCliente=c.id)
                db.add(v)
                vehiculo_placas.append(placa)
            await db.commit()

        # Inteligencia: Si no hay placas, buscar existentes
        if not vehiculo_placas:
            res_v = await db.execute(select(Vehiculo.placa))
            vehiculo_placas = [r[0] for r in res_v.all()]
            if vehiculo_placas:
                print(f">> Detectados {len(vehiculo_placas)} vehículos existentes en BD.")

        # Si seguimos sin vehículos y queremos emergencias, debemos crear algunos sí o sí
        if not vehiculo_placas and emergencias > 0:
            print(">> No hay vehículos en BD. Generando 5 de emergencia para proceder...")
            for _ in range(5):
                c = Cliente(nombre=fake.name(), correo=fake.unique.email(), contrasena=hash_password("cliente123"))
                db.add(c)
                await db.flush()
                placa = generate_plate()
                db.add(Vehiculo(placa=placa, marca="Demo", modelo="Test", anio=2024, idCliente=c.id))
                vehiculo_placas.append(placa)
            await db.commit()

        # 3. Emergencias y Tráfico de IA
        if emergencias > 0:
            print(f">> Detectando talleres para posicionamiento inteligente...")
            # Obtener talleres con coordenadas para el "jitter"
            res_w = await db.execute(select(Taller).where(Taller.latitud != None))
            workshop_pool = res_w.scalars().all()
            
            if not workshop_pool:
                print("!! ADVERTENCIA: No hay talleres con GPS. Las coordenadas serán aleatorias.")
            
            print(f">> Lanzando {emergencias} Emergencias al motor de IA (CONCURRENTE)...")
            emergencia_objs = []
            est_init_id = (await db.execute(select(Estado.id).where(Estado.nombre == "INICIADA"))).scalar_one_or_none()
            
            for i in range(emergencias):
                # 3.a Selección de Vehículo y Cliente
                placa = random.choice(vehiculo_placas)
                res_c = await db.execute(select(Vehiculo.idCliente).where(Vehiculo.placa == placa))
                cid = res_c.scalar()
                
                # 3.b Posicionamiento inteligente
                if workshop_pool:
                    target = random.choice(workshop_pool)
                    # Jitter de aprox 0.05 a 0.2 grados (~5 a 20km)
                    lat = target.latitud + random.uniform(-0.15, 0.15)
                    lon = target.longitud + random.uniform(-0.15, 0.15)
                else:
                    lat = float(fake.latitude())
                    lon = float(fake.longitude())

                e = Emergencia(
                    descripcion=f"Incidente Real {fake.word()}",
                    texto_adicional=random.choice(PROMPTS_EMERGENCIA),
                    direccion=fake.address(),
                    latitud=lat, 
                    longitud=lon,
                    hora=datetime.now().time(),
                    idTaller=None, # IMPORTANTE: Sin asignar para Discovery
                    idPrioridad=1, idCategoria=1, # Temporales hasta IA
                    idCliente=cid, placaVehiculo=placa
                )
                db.add(e)
                await db.flush()
                db.add(HistorialEstado(idEmergencia=e.id, idEstado=est_init_id))
                emergencia_objs.append(e)
            
            await db.commit()
            
            # PROCESAMIENTO PARALELO DE IA
            tasks = [process_ia_worker(AsyncSessionLocal, e, use_real_ia) for e in emergencia_objs]
            await asyncio.gather(*tasks)

            # 4. Enriquecimiento final limitado (Solo Evidencias) - Lifecycle omitido para Discovery Test
            print(">> Generando evidencias para las emergencias...")
            async with AsyncSessionLocal() as db_final:
                for e in emergencia_objs:
                    await seed_evidencia(db_final, e.id)
                await db_final.commit()

    print(f"\n{'='*20} POBLADO TOTAL FINALIZADO {'='*20}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--talleres", type=int, default=5)
    parser.add_argument("--clientes", type=int, default=10)
    parser.add_argument("--emergencias", type=int, default=10)
    parser.add_argument("--real-ia", action="store_true", help="Usa la API real de OpenRouter")
    args = parser.parse_args()
    asyncio.run(seed_world_builder(args.talleres, args.clientes, args.emergencias, use_real_ia=args.real_ia))
