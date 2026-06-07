import os
import sys
from pathlib import Path
import asyncio
import questionary
from datetime import datetime

# Asegurar path
current_dir = Path(__file__).resolve().parent
backend_path = current_dir.parent.parent.parent.parent.parent / "backend"
backend_str = str(backend_path.absolute())

if backend_str not in sys.path:
    sys.path.insert(0, backend_str)

from app.db.session import AsyncSessionLocal
from app.db.base import Cliente, Vehiculo
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.services import ai_service
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.schemas.emergencia import EmergenciaCreate
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.services import emergencia_service
from app.core.context import set_user_context

async def simular_transaccion_emergencia():
    print("=========================================================")
    print("  SIMULADOR DE TRANSACCIONES DE EMERGENCIA (COMO CLIENTE) ")
    print("=========================================================")
    print("Este módulo simula la creación de una emergencia desde la app móvil.\n")

    async with AsyncSessionLocal() as db:
        # 1. Seleccionar Cliente
        result = await db.execute(select(Cliente).options(selectinload(Cliente.vehiculos)))
        clientes = result.scalars().all()

        if not clientes:
            print("❌ No hay clientes en la base de datos.")
            return

        cliente_choices = [f"[{c.id}] {c.nombre} ({c.correo})" for c in clientes]
        cliente_seleccionado_str = await questionary.select(
            "Selecciona el cliente que va a reportar la emergencia:",
            choices=cliente_choices
        ).ask_async()

        if not cliente_seleccionado_str:
            return

        cliente_id = int(cliente_seleccionado_str.split("]")[0].replace("[", ""))
        cliente = next(c for c in clientes if c.id == cliente_id)

        # 2. Seleccionar Vehículo
        if not cliente.vehiculos:
            print("❌ Este cliente no tiene vehículos registrados.")
            return

        vehiculo_choices = [f"[{v.placa}] {v.marca} {v.modelo} ({v.año})" for v in cliente.vehiculos]
        vehiculo_seleccionado_str = await questionary.select(
            "Selecciona el vehículo del cliente:",
            choices=vehiculo_choices
        ).ask_async()

        if not vehiculo_seleccionado_str:
            return

        placa_vehiculo = vehiculo_seleccionado_str.split("]")[0].replace("[", "")

        # 3. Texto Crudo (Simulación de Whisper)
        texto_crudo = await questionary.text(
            "Escribe el reporte crudo del problema (como si lo hablaras por voz):"
        ).ask_async()

        if not texto_crudo:
            return

        # 4. Ubicación de la Emergencia
        lat_str = await questionary.text("Latitud (ej. -17.7833):").ask_async()
        lon_str = await questionary.text("Longitud (ej. -63.1821):").ask_async()
        direccion = await questionary.text("Dirección aproximada:").ask_async()

        try:
            lat = float(lat_str) if lat_str else -17.7833
            lon = float(lon_str) if lon_str else -63.1821
            direccion = direccion if direccion else "Dirección simulada"
        except ValueError:
            print("❌ Coordenadas inválidas. Usando por defecto.")
            lat, lon = -17.7833, -63.1821
            direccion = "Dirección simulada"

        print("\n⚙️  Enviando reporte a la base de datos y a la IA...")
        
        # Simular contexto de usuario autenticado
        set_user_context(cliente.id)

        # Crear esquema de entrada
        data = EmergenciaCreate(
            descripcion=texto_crudo,
            texto_adicional=texto_crudo,
            latitud=lat,
            longitud=lon,
            direccion=direccion,
            hora=datetime.now().time(),
            placaVehiculo=placa_vehiculo,
            evidencias_urls=[]
        )

        try:
            # Ejecutar el servicio que llama a la IA y guarda en BD
            emergencia_creada = await emergencia_service.reportar_emergencia(data, cliente.id, db)
            print(f"\n✅ ¡Emergencia creada exitosamente con ID {emergencia_creada.id}!")
            print(f"📍 Coordenadas: ({emergencia_creada.latitud}, {emergencia_creada.longitud})")
            print(f"📝 Categoría asignada (por IA): {emergencia_creada.idCategoria}")
            print(f"🚨 Prioridad asignada (por IA): {emergencia_creada.idPrioridad}")
            
            print("\n=========================================================")
            print("Ahora puedes revisar los logs del Radar en tu VPS o hacer la consulta.")
            print("=========================================================\n")

        except Exception as e:
            print(f"\n❌ Error al crear la emergencia: {e}")

if __name__ == "__main__":
    asyncio.run(simular_transaccion_emergencia())
