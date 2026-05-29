import os
import subprocess
import platform
import sys
import threading

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
    return app_host

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
