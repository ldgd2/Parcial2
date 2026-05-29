import os
import json

def sync():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_file = os.path.join(root_dir, ".env")
    config_file = os.path.join(root_dir, "frontend", "src", "assets", "config.json")

    ip = "localhost"
    port = "8000"

    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith("APP_HOST="):
                    ip = line.split("=")[1].strip()
                if line.startswith("APP_PORT_BACKEND="):
                    port = line.split("=")[1].strip()

    config = {
        "apiUrl": f"http://{ip}:{port}/api/v1"
    }
    
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Sincronizado assets/config.json con Backend en {ip}:{port}")

if __name__ == "__main__":
    sync()
