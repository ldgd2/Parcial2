import asyncio
import os
import sys

# Agregamos la raiz para que encuentre app
_root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(_root_dir)

from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.services.ai_service import analizar_transcripcion_whisper

async def run_test():
    try:
        resultado = await analizar_transcripcion_whisper(
            texto_crudo="El auto no enciende, hace un ruido de clac clac y las luces del tablero parpadean. Ayuda",
            categorias_disponibles=[{"id": 1, "nombre": "Motor"}, {"id": 2, "nombre": "Eléctrico"}],
            prioridades_disponibles=[{"id": 1, "nombre": "Baja"}, {"id": 2, "nombre": "Alta"}],
            vehiculo_info="Toyota Corolla 2020",
            evidencias_urls=[]
        )
        print("EXITO:")
        print(resultado.model_dump_json(indent=2))
    except Exception as e:
        import traceback
        print("ERROR:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_test())
