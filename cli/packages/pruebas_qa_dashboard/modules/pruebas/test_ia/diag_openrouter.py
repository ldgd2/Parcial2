import httpx
import os
import json
import sys
from dotenv import load_dotenv

# Agregamos la ruta base del backend para poder importar si fuera necesario
# Y buscar el .env en la raiz
_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(_root_dir, ".env"))

API_KEY = os.getenv("OPENROUTER_API_KEY")

async def check_key():
    if not API_KEY:
        print("[ERROR]: No se encontró OPENROUTER_API_KEY en el archivo .env")
        return

    print(f"[SCAN]: Validando API Key: {API_KEY[:10]}...{API_KEY[-5:]}")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            # 1. Consultar estado de la Key
            response = await client.get("https://openrouter.ai/api/v1/key", headers=headers)
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                print("\n[OK] Resumen de OpenRouter:")
                limit = data.get('limit')
                usage = data.get('usage')
                
                print(f"   - Limite de Creditos: ${limit if limit is not None else 'N/A'}")
                print(f"   - Uso Actual: ${usage if usage is not None else '0'}")
                
                if limit is None and usage is None:
                    print("\n[DEBUG]: Respuesta completa de OpenRouter:")
                    print(json.dumps(data, indent=2))
                
                # Calcular balance
                if limit is not None and usage is not None:
                    balance = limit - usage
                    print(f"   - Balance Restante: ${balance:.4f}")
                    
                    if balance < 0.01:
                        print("\n[WARN]: Tu saldo es casi cero o negativo. OpenRouter bloqueara las peticiones.")
                    elif limit < 10:
                        print("\n[INFO]: Tienes menos de $10.00 en creditos. Límite: 50 peticiones/dia para modelos FREE.")
                else:
                    print("\n[INFO]: No se detectaron limites de credito. Si estas usando modelos 'free', el limite suele ser de 50 peticiones diarias por IP/Key si no has cargado al menos $10 USD.")
                
            elif response.status_code == 401:
                print("\n[ERROR] 401: La API Key no es válida.")
            else:
                print(f"\n[ERROR] {response.status_code}: {response.text}")

        except Exception as e:
            print(f"\n[ERROR] de conexión: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_key())
