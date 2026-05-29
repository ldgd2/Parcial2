import os
import platform
import getpass
import socket
import urllib.request
import subprocess
import time
import sys

def get_public_ip():
    try:
        return urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
    except:
        return "localhost"

def edit_network_config(port_back):
    public_ip = get_public_ip()
    update_env_file(public_ip, port_back)
    sync_env_to_angular(public_ip, port_back)
    print("Configuración de red actualizada y sincronizada.")

def setup_vps_services(port_back, port_front):
    public_ip = get_public_ip()
    update_env_file(public_ip, port_back)
    sync_env_to_angular(public_ip, port_back)

    cwd = os.getcwd()
    user = getpass.getuser()
    python_exe = sys.executable
    
    if not os.path.exists("deploy"):
        os.makedirs("deploy")
    
    backend_svc = f"""[Unit]
Description=Servicio Taller Backend (Dev Mode)
After=network.target

[Service]
User={user}
WorkingDirectory={cwd}/backend
EnvironmentFile={cwd}/.env
ExecStart={python_exe} -m uvicorn app.main:app --host 0.0.0.0 --port {port_back}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
    with open("deploy/taller-backend.service", "w") as f:
        f.write(backend_svc)

    frontend_svc = f"""[Unit]
Description=Servicio Taller Frontend (Angular Dev)
After=network.target

[Service]
User={user}
WorkingDirectory={cwd}/frontend
ExecStartPre={python_exe} {cwd}/scripts/sync_env.py
ExecStart=/usr/bin/npm start -- --host 0.0.0.0 --port {port_front} --disable-host-check
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    with open("deploy/taller-frontend.service", "w") as f:
        f.write(frontend_svc)

    print("Servicios GENERADOS e .env Sincronizado.")

def install_services(public_ip, port_back, port_front):
    cwd = os.getcwd()
    if platform.system() != "Windows":
        os.system("sudo systemctl stop taller-backend taller-frontend 2>/dev/null")
        os.system("sudo systemctl disable taller-backend taller-frontend 2>/dev/null")
        os.system(f"sudo cp {cwd}/deploy/taller-backend.service /etc/systemd/system/")
        os.system(f"sudo cp {cwd}/deploy/taller-frontend.service /etc/systemd/system/")
        os.system("sudo systemctl daemon-reload")
        os.system("sudo systemctl enable taller-backend taller-frontend")
        os.system("sudo systemctl restart taller-backend taller-frontend")
        print(f"Servicios levantados en modo DEV.\nBackend: http://{public_ip}:{port_back}\nFrontend: http://{public_ip}:{port_front}")
    else:
        print("Instrucciones: Copia los archivos de ./deploy/ a /etc/systemd/system/ en tu Ubuntu.")

def update_env_file(ip, port):
    lines = []
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            lines = f.readlines()
    
    lines = [l for l in lines if not l.startswith("APP_HOST=") and not l.startswith("APP_PORT_BACKEND=")]
    lines.append(f"APP_HOST={ip}\n")
    lines.append(f"APP_PORT_BACKEND={port}\n")
    
    with open(".env", "w") as f:
        f.writelines(lines)
    print("Archivo .env actualizado con la IP y Puerto.")

def sync_env_to_angular(ip, port):
    config_path = "frontend/src/assets/config.json"
    import json
    config = {
        "apiUrl": f"http://{ip}:{port}/api/v1"
    }
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Assets/config.json sincronizado con Backend en {ip}:{port}")

def check_services():
    if platform.system() == "Windows":
        print("Esta opción solo funciona en Linux/VPS.")
        return
    
    os.system("clear")
    print("ESTADO DE LOS DAEMONS DE EJECUCIÓN")
    os.system("systemctl status taller-backend --no-pager")
    print("-" * 30)
    os.system("systemctl status taller-frontend --no-pager")

def restart_services():
    if platform.system() == "Windows":
        print("Esta opción solo funciona en Linux/VPS.")
        return
    
    print("Reiniciando servicios de ejecución...")
    os.system("sudo systemctl restart taller-backend taller-frontend")
    print("Servicios reiniciados.")

def delete_services():
    if platform.system() == "Windows":
        print("Esta opción solo funciona en Linux/VPS.")
        return
        
    print("Deteniendo y eliminando servicios...")
    os.system("sudo systemctl stop taller-backend taller-frontend 2>/dev/null")
    os.system("sudo systemctl disable taller-backend taller-frontend 2>/dev/null")
    os.system("sudo rm -f /etc/systemd/system/taller-backend.service")
    os.system("sudo rm -f /etc/systemd/system/taller-frontend.service")
    os.system("sudo systemctl daemon-reload")
    print("Servicios eliminados correctamente del sistema.")

def view_logs(target):
    if platform.system() == "Windows":
        print("Esta opción solo funciona en Linux/VPS.")
        return
    
    print(f"Mostrando logs en TIEMPO REAL de taller-{target} (Presiona Ctrl+C para salir)")
    try:
        os.system(f"sudo journalctl -u taller-{target}.service -f -n 100")
    except KeyboardInterrupt:
        pass
    print()
