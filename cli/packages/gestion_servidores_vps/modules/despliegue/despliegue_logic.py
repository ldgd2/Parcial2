import os
import getpass
import platform
import socket
import urllib.request

def get_public_ip():
    try:
        return urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
    except:
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return "127.0.0.1"

def execute_logic(domain, port_backend, port_frontend):
    is_windows = platform.system() == "Windows"
    cwd = os.getcwd()
    user = getpass.getuser() if not is_windows else "ubuntu"
    
    if not os.path.exists("deploy"):
        os.makedirs("deploy")

    # --- Generar Servicio Backend ---
    backend_service = f"""[Unit]
Description=Backend FastAPI - Taller Movil
After=network.target

[Service]
User={user}
Group=www-data
WorkingDirectory={cwd}/backend
Environment="PATH={cwd}/backend/.venv/bin"
EnvironmentFile={cwd}/.env
ExecStart={cwd}/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port {port_backend} --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
"""
    with open("deploy/taller-backend.service", "w") as f:
        f.write(backend_service)
    print(f"Generado: deploy/taller-backend.service (Puerto {port_backend})")

    # --- Generar Configuración Nginx ---
    nginx_config = f"""server {{
    listen {port_frontend};
    server_name {domain};

    # Backend API
    location /api/v1/ {{
        proxy_pass http://localhost:{port_backend};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }}

    # Frontend Angular
    location / {{
        root {cwd}/frontend/dist/frontend/browser;
        index index.html;
        try_files $uri $uri/ /index.html;
    }}
}}
"""
    with open("deploy/taller-nginx.conf", "w") as f:
        f.write(nginx_config)
    print(f"Generado: deploy/taller-nginx.conf (Puerto {port_frontend})")

    # --- Mostrar Instrucciones ---
    print(f"\nINSTRUCCIONES PARA TU VPS (UBUNTU):\n")
    print(f"1. Copia los archivos a sus carpetas correspondientes:")
    print(f"   sudo cp {cwd}/deploy/taller-backend.service /etc/systemd/system/")
    print(f"   sudo cp {cwd}/deploy/taller-nginx.conf /etc/nginx/sites-available/taller\n")
    print(f"2. Activa el sitio en Nginx y reinicia:")
    print(f"   sudo ln -s /etc/nginx/sites-available/taller /etc/nginx/sites-enabled/")
    print(f"   sudo nginx -t && sudo systemctl restart nginx\n")
    print(f"3. Inicia el servicio del Backend:")
    print(f"   sudo systemctl daemon-reload")
    print(f"   sudo systemctl enable taller-backend")
    print(f"   sudo systemctl start taller-backend\n")
    print(f"Proyecto configurado para responder en: http://{domain}:{port_frontend}\n")
