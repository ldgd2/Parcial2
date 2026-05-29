import os
import socket
import re
import json

def get_local_ip():
    """Detecta la IP local de la maquina en la red."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def update_env_variable(key, value):
    """Actualiza o agrega una variable en el .env de la raíz."""
    env_path = ".env"
    if not os.path.exists(env_path):
        return
    
    lines = []
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            found = True
            break
    if not found:
        lines.append(f"{key}={value}\n")
        
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def configure_network_logic(target_host, target_port):
    # 1. Actualizar .env en la raíz
    env_path = ".env"
    if os.path.exists(env_path):
        update_env_variable("APP_HOST", target_host)
        update_env_variable("APP_PORT_BACKEND", target_port)
        print(f"[OK] APP_HOST y APP_PORT_BACKEND actualizados a {target_host}:{target_port} en .env")

    # 2. Actualizar Frontend environment.ts
    front_env = os.path.join("frontend", "src", "environments", "environment.ts")
    if os.path.exists(front_env):
        with open(front_env, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regex para reemplazar http://[host]:[port]/api/v1
        new_content = re.sub(r'(http://)[^/:]+(:\d+)?(/api/v1)', r'\g<1>' + target_host + f':{target_port}' + r'\g<3>', content)
        with open(front_env, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"[OK] Frontend API URL actualizado a http://{target_host}:{target_port} en environment.ts")

    # 3. Actualizar Frontend config.json
    config_json_path = os.path.join("frontend", "src", "assets", "config.json")
    config_dir = os.path.dirname(config_json_path)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)
        
    config_data = {}
    if os.path.exists(config_json_path):
        try:
            with open(config_json_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except Exception:
            pass
            
    config_data["apiUrl"] = f"http://{target_host}:{target_port}/api/v1"
    with open(config_json_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2)
    print(f"[OK] Frontend API URL actualizado a http://{target_host}:{target_port}/api/v1 en config.json")
