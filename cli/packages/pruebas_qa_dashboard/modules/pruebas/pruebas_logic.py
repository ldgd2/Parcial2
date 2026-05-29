import urllib.request
import urllib.error
import json
import os
import platform
import subprocess
import sys

def ping_backend():
    try:
        req = urllib.request.Request("http://localhost:8000/api/v1/")
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            data = json.loads(response.read().decode())
            
            if status == 200:
                return {"ok": True, "status": status, "data": data.get('message', data)}
            else:
                return {"ok": False, "error": f"[ATENCION] Backend respondio con codigo {status}: {data}"}
                
    except urllib.error.URLError as e:
        return {"ok": False, "error": f"De Conexion: {e.reason}\nAsegurate de que el backend ha sido levantado usando:\npython taller.py run backend"}

def test_frontend():
    print("Lanzando Pruebas (Tests) del Frontend...")
    is_windows = platform.system() == "Windows"
    ng_cmd = "ng.cmd" if is_windows else "ng"
    
    os.chdir("frontend")
    try:
        subprocess.run([ng_cmd, "test", "--watch=false"], check=True)
        print("Pruebas finalizadas.")
    except FileNotFoundError:
        print("[ERROR] No se encontro 'ng'. Ejecutaste 'python taller.py setup frontend'?")
    finally:
        os.chdir("..")

def test_ia():
    print("Lanzando Pruebas (Tests) de Inteligencia Artificial...")
    sys_exe = sys.executable
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_ia_dir = os.path.join(script_dir, "test_ia")
    
    print("\nMódulo: Transcripción (faster-whisper)")
    subprocess.run([sys_exe, os.path.join(test_ia_dir, "test_whisper.py")])
    
    print("\nMódulo: Análisis Inteligente (OpenRouter)")
    subprocess.run([sys_exe, os.path.join(test_ia_dir, "test_openrouter.py")])

def test_diag_ai():
    sys_exe = sys.executable
    script_dir = os.path.dirname(os.path.abspath(__file__))
    diag_script = os.path.join(script_dir, "test_ia", "diag_openrouter.py")
    subprocess.run([sys_exe, diag_script])

def send_notification_logic(tipo, titulo, cuerpo, extra_data, target_token=None, target_user_id=None):
    try:
        base_url = "http://localhost:8000/api/v1/notificaciones"
        
        if tipo == "Broadcast (A todos)":
            url = f"{base_url}/test-broadcast?titulo={urllib.parse.quote(titulo)}&cuerpo={urllib.parse.quote(cuerpo)}"
            data_json = json.dumps(extra_data).encode()
            req = urllib.request.Request(url, data=data_json, method="POST", headers={"Content-Type": "application/json"})
        elif tipo == "Personalizada (A un Usuario)":
            url = f"{base_url}/test-personalizada"
            payload = {"user_id": int(target_user_id), "titulo": titulo, "cuerpo": cuerpo}
            data_json = json.dumps(payload).encode()
            req = urllib.request.Request(url, data=data_json, method="POST", headers={"Content-Type": "application/json"})
        else: # Directa (Por Token)
            url = f"{base_url}/test-token?token={urllib.parse.quote(target_token)}&titulo={urllib.parse.quote(titulo)}&cuerpo={urllib.parse.quote(cuerpo)}"
            data_json = json.dumps(extra_data).encode()
            req = urllib.request.Request(url, data=data_json, method="POST", headers={"Content-Type": "application/json"})

        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            return {"ok": True, "msg": res_data.get('message')}
    except Exception as e:
        return {"ok": False, "error": str(e)}
