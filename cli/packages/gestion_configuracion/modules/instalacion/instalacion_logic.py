import os
import subprocess
import platform
import sys
import shutil

def setup_backend():
    pip_cmd = [sys.executable, "-m", "pip"]
    try:
        subprocess.run([*pip_cmd, "install", "--upgrade", "pip"], check=False, capture_output=True)
    except:
        pass
        
    subprocess.run([*pip_cmd, "install", "-r", os.path.join("backend", "requirements.txt")], check=True)

def setup_frontend():
    if not os.path.exists("frontend"):
        print("Carpeta frontend no encontrada, saltando.")
        return
        
    os.chdir("frontend")
    is_windows = platform.system() == "Windows"
    npm_cmd = "npm.cmd" if is_windows else "npm"
    
    result = subprocess.run([npm_cmd, "install"])
    
    if result.returncode != 0:
        print("Conflictos detectados. Reintentando con --legacy-peer-deps...")
        subprocess.run([npm_cmd, "install", "--legacy-peer-deps"])
        
    os.chdir("..")

def install_deps():
    setup_backend()
    setup_frontend()

def setup_env():
    root_env = ".env"
    backend_example = os.path.join("backend", ".env.example")
    
    if not os.path.exists(root_env) and os.path.exists(backend_example):
        shutil.copyfile(backend_example, root_env)
        generate_secret_keys(root_env)
    elif os.path.exists(root_env):
        generate_secret_keys(root_env)

def generate_secret_keys(env_path):
    import secrets
    
    if not os.path.exists(env_path):
        return
        
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    updated = False
    for i, line in enumerate(lines):
        if line.startswith("SECRET_KEY=") and ("cambia_esto" in line or "secret_key_placeholder" in line):
            new_key = secrets.token_hex(32)
            lines[i] = f"SECRET_KEY={new_key}\n"
            updated = True
            
    if updated:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

def setup_redis():
    # Placeholder para docker run redis
    print("Iniciando contenedor de Redis via Docker...")
    subprocess.run(["docker", "run", "-d", "--name", "taller_redis", "-p", "6379:6379", "redis:alpine"], check=False)
