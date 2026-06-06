import requests
import json
import time
from typing import Optional

# Configuración
API_BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 60


class EmergenciaAPIClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.session = requests.Session()

    def login(self, correo: str, contrasena: str) -> bool:
        """Autenticarse con las credenciales del cliente"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"correo": correo, "contrasena": contrasena, "rol": "cliente"},
                timeout=TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            self.token = data.get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            print(f"✅ Autenticado como {correo}")
            return True
        except Exception as e:
            print(f"❌ Error al autenticarse: {e}")
            return False

    def crear_emergencia(self, datos: dict) -> Optional[dict]:
        """Crear una emergencia consumiendo la API"""
        try:
            response = self.session.post(
                f"{self.base_url}/emergencias/reportar",
                json=datos,
                timeout=TIMEOUT
            )
            response.raise_for_status()
            emergencia = response.json()
            print(f"✅ Emergencia creada: {emergencia.get('id')}")
            return emergencia
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al crear emergencia: {e}")
            if hasattr(e.response, 'text'):
                print(f"   Respuesta: {e.response.text}")
            return None

    def close(self):
        """Cerrar la sesión"""
        self.session.close()


def crear_emergencias_desde_api():
    """Crear emergencias consumiendo la API con usuarios del seeder"""
    
    import random
    from datetime import datetime, timedelta

    coordenadas_base = [
        (-17.814942, -63.206901, "Av. Radial 17 y medio"),
        (-17.826528, -63.198833, "Av. Santos Dumont y 4to Anillo"),
        (-17.787909, -63.185986, "Equipetrol Norte"),
        (-17.807563, -63.169530, "Av. Virgen de Cotoca"),
        (-17.826666, -63.221352, "Doble Vía a La Guardia"),
        (-17.775000, -63.195000, "Av. Banzer y 3er Anillo") # Cerca
    ]

    descripciones = [
        ("Falla en motor, no enciende", "Auto no responde al encendido, hace ruido raro"),
        ("Pinchazo de llanta", "Llanta delantera derecha reventada por bache"),
        ("Falla eléctrica", "Batería muerta, las luces no prenden"),
        ("Problema en frenos", "El pedal de freno está muy duro y no frena"),
        ("A/C no funciona", "Sistema de aire acondicionado echa aire caliente"),
        ("Recalentamiento de motor", "Sale humo del capó, temperatura al máximo"),
        ("Falla de transmisión", "La caja de cambios no entra a segunda"),
        ("Problema de suspensión", "El auto suena mucho al pasar rompemuelles")
    ]

    # Mapeo estricto de clientes a sus placas registradas
    clientes_vehiculos = [
        ("ana.maria@email.com", "ABC-123"),
        ("ana.maria@email.com", "DEF-456"),
        ("roberto.f@email.com", "GHI-789"),
        ("roberto.f@email.com", "JKL-012"),
        ("maria.garcia@email.com", "PQR-678"),
        ("pedro.lopez@email.com", "STU-901")
    ]

    emergencias_data = []
    
    # Generar 6 emergencias procedimentales respetando la relación persona-placa
    for i, (correo, placa) in enumerate(clientes_vehiculos):
        coord = random.choice(coordenadas_base)
        desc = random.choice(descripciones)
        hora_generada = (datetime.strptime("08:00:00", "%H:%M:%S") + timedelta(minutes=random.randint(0, 600))).strftime("%H:%M:%S")
        
        emergencias_data.append({
            "correo_cliente": correo,
            "datos": {
                "descripcion": desc[0],
                "texto_adicional": desc[1],
                "direccion": coord[2],
                "latitud": coord[0],
                "longitud": coord[1],
                "placaVehiculo": placa,
                "hora": hora_generada
            }
        })


    print("\n🚨 Creando emergencias desde API...\n")

    clientes_autenticados = {}
    creadas = 0
    errores = 0

    for emerg in emergencias_data:
        correo = emerg["correo_cliente"]

        # Reutilizar cliente si ya está autenticado
        if correo not in clientes_autenticados:
            client = EmergenciaAPIClient()
            if client.login(correo, "cliente123"):
                clientes_autenticados[correo] = client
            else:
                print(f"❌ No se pudo autenticar {correo}, saltando emergencia")
                errores += 1
                continue
        
        client = clientes_autenticados[correo]
        if client.crear_emergencia(emerg["datos"]):
            creadas += 1
        else:
            errores += 1
            
        print("Esperando 15 segundos para no saturar la IA...")
        time.sleep(15)

    # Cerrar todas las sesiones
    for client in clientes_autenticados.values():
        client.close()

    print(f"\n📊 Resumen:")
    print(f"  ✅ Emergencias creadas: {creadas}")
    print(f"  ❌ Errores: {errores}")
    print(f"  Total: {len(emergencias_data)}\n")


if __name__ == "__main__":
    crear_emergencias_desde_api()
