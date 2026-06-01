import os
import subprocess
import platform
import sys
import threading
import re

def get_app_host():
    app_host = "localhost"
    try:
        env_path = ".env"
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith("APP_HOST="):
                        app_host = line.split("=")[1].strip()
                        break
    except:
        pass
    sync_ip_to_clients(app_host)
    return app_host

def sync_ip_to_clients(ip: str):
    print(f"[*] Sincronizando IP {ip} en Angular y Flutter...")
    
    # 1. Angular environment.ts
    env_ts_path = os.path.join("frontend", "src", "environments", "environment.ts")
    if os.path.exists(env_ts_path):
        with open(env_ts_path, 'r') as f: content = f.read()
        content = re.sub(r"apiUrl:\s*'http://[^:]+:8000/api/v1'", f"apiUrl: 'http://{ip}:8000/api/v1'", content)
        with open(env_ts_path, 'w') as f: f.write(content)

    # 2. Angular environment.prod.ts
    env_prod_path = os.path.join("frontend", "src", "environments", "environment.prod.ts")
    if os.path.exists(env_prod_path):
        with open(env_prod_path, 'r') as f: content = f.read()
        content = re.sub(r"apiUrl:\s*'http://[^:]+:8000/api/v1'", f"apiUrl: 'http://{ip}:8000/api/v1'", content)
        with open(env_prod_path, 'w') as f: f.write(content)

    # 3. Angular config.json (Usado en runtime por APP_INITIALIZER)
    config_json_path = os.path.join("frontend", "src", "assets", "config.json")
    if os.path.exists(config_json_path):
        with open(config_json_path, 'r') as f: content = f.read()
        content = re.sub(r'"apiUrl":\s*"http://[^:]+:8000/api/v1"', f'"apiUrl": "http://{ip}:8000/api/v1"', content)
        with open(config_json_path, 'w') as f: f.write(content)

    # 3. Flutter api_client.dart
    api_client_path = os.path.join("tallermovil", "lib", "core", "network", "api_client.dart")
    if os.path.exists(api_client_path):
        with open(api_client_path, 'r') as f: content = f.read()
        content = re.sub(r"serverUrl\s*=\s*'http://[^:]+:\d+'", f"serverUrl = 'http://{ip}:8000'", content)
        with open(api_client_path, 'w') as f: f.write(content)

    # 4. Flutter web_socket_service.dart
    ws_service_path = os.path.join("tallermovil", "lib", "core", "network", "web_socket_service.dart")
    if os.path.exists(ws_service_path):
        with open(ws_service_path, 'r') as f: content = f.read()
        content = re.sub(r"baseUrl\s*=\s*'ws://[^:]+:8000'", f"baseUrl = 'ws://{ip}:8000'", content)
        with open(ws_service_path, 'w') as f: f.write(content)


def run_backend():
    app_host = get_app_host()
    print(f"Iniciando Backend (FastAPI) en http://{app_host}:8000\nUsa Ctrl+C para salir")
    
    os.chdir("backend")
    subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
    os.chdir("..")

def run_frontend():
    print("Iniciando Frontend (Angular) en http://localhost:4200\nUsa Ctrl+C para salir")
    is_windows = platform.system() == "Windows"
    npm_cmd = "npm.cmd" if is_windows else "npm"
    
    os.chdir("frontend")
    try:
        subprocess.run([npm_cmd, "start"])
    except KeyboardInterrupt:
        pass
    finally:
        os.chdir("..")

def run_all():
    app_host = get_app_host()
    print(f"Iniciando TODO de forma concurrente...\nBackend: http://{app_host}:8000\nFrontend: http://{app_host}:4200\nSigue los logs de ambos (Ctrl+C para salir)")
    
    is_windows = platform.system() == "Windows"
    npm_cmd = "npm.cmd" if is_windows else "npm"
    
    def run_back():
        os.chdir("backend")
        subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
        
    def run_front():
        os.chdir("frontend")
        subprocess.run([npm_cmd, "start"])

    tb = threading.Thread(target=run_back)
    tf = threading.Thread(target=run_front)
    
    tb.start()
    tf.start()
    
    try:
        tb.join()
        tf.join()
    except KeyboardInterrupt:
        print("\nApagando servidores...")
