import os
import secrets

def update_env_variable(filepath, key, new_value):
    if not os.path.exists(filepath):
        print(f"ERROR: No existe {filepath}")
        return

    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={new_value}\n"
            found = True
            break
            
    if not found:
        lines.append(f"{key}={new_value}\n")
        
    with open(filepath, 'w') as f:
        f.writelines(lines)

def config_db(user, password, host, port, dbname):
    env_file = ".env"
    if not os.path.exists(env_file):
        print("ERROR: El archivo .env no existe.")
        return
        
    update_env_variable(env_file, "DB_USER", user)
    update_env_variable(env_file, "DB_PASSWORD", password)
    update_env_variable(env_file, "DB_HOST", host)
    update_env_variable(env_file, "DB_PORT", port)
    update_env_variable(env_file, "DB_NAME", dbname)

def config_jwt():
    env_file = ".env"
    if not os.path.exists(env_file):
        print("ERROR: El archivo .env no existe.")
        return
        
    new_secret = secrets.token_hex(32)
    update_env_variable(env_file, "SECRET_KEY", new_secret)
