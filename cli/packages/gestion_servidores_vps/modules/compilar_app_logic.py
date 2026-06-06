import os
import subprocess
import requests
from rich.console import Console

console = Console()

def compilar_y_publicar():
    console.print("\n[bold cyan]=== Compilación y Publicación de App Móvil (Flutter) ===[/bold cyan]\n")
    
    # 1. Leer host y puerto del .env raíz
    app_host = "localhost"
    port_backend = "8000"
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("APP_HOST="):
                    app_host = line.split("=")[1].strip()
                elif line.startswith("BACKEND_PORT="):
                    port_backend = line.split("=")[1].strip()
    except Exception as e:
        console.print(f"[yellow]Advertencia: No se pudo leer .env ({e}). Usando valores por defecto.[/yellow]")
    
    backend_url = f"http://{app_host}:{port_backend}"
    console.print(f"[bold green]▶[/bold green] Backend detectado: [bold white]{backend_url}[/bold white]")
    
    # 2. Pedir versión y notas
    import questionary
    version = questionary.text("Ingresa la versión de este release (ej. 1.0.0):").ask()
    if not version:
        console.print("[red]Versión requerida. Cancelando.[/red]")
        return
        
    changelog = questionary.text("Notas de la versión (changelog):").ask()
    
    # 3. Compilar Flutter
    console.print("\n[bold yellow]Compilando APK (Release)... Esto tomará unos minutos.[/bold yellow]")
    flutter_dir = os.path.join(os.getcwd(), "tallermovil")
    
    if not os.path.exists(flutter_dir):
        console.print("[red]Error: Carpeta 'tallermovil' no encontrada.[/red]")
        return
        
    compile_cmd = [
        "flutter.bat" if os.name == 'nt' else "flutter", "build", "apk", "--release", 
        f"--dart-define=BACKEND_URL={backend_url}"
    ]
    
    # Ejecutar compilación
    try:
        subprocess.run(compile_cmd, cwd=flutter_dir, check=True)
    except subprocess.CalledProcessError as e:
        console.print(f"\n[red]Error durante la compilación: {e}[/red]")
        return
    except FileNotFoundError:
        console.print("\n[red]Error: Flutter no está instalado o no está en el PATH.[/red]")
        return
        
    console.print("[bold green]✔ Compilación Exitosa.[/bold green]")
    
    # 4. Enviar al Backend
    apk_path = os.path.join(flutter_dir, "build", "app", "outputs", "flutter-apk", "app-release.apk")
    
    if not os.path.exists(apk_path):
        console.print("[red]Error: No se encontró el APK generado.[/red]")
        return
        
    console.print(f"\n[bold yellow]Subiendo APK al backend ({backend_url})...[/bold yellow]")
    publish_url = f"{backend_url}/api/v1/apps/publish"
    
    try:
        with open(apk_path, "rb") as f:
            files = {"file": (f"tallermovil_v{version}.apk", f, "application/vnd.android.package-archive")}
            data = {"version": version, "changelog": changelog}
            
            response = requests.post(publish_url, files=files, data=data)
            
            if response.status_code == 200:
                console.print("\n[bold green]✔ ¡App publicada con éxito![/bold green]")
                console.print(f"Descarga disponible en: [bold cyan]{backend_url}/api/v1/apps/download/latest[/bold cyan]")
            else:
                console.print(f"\n[red]Error al publicar: {response.text}[/red]")
    except requests.exceptions.ConnectionError:
        console.print("\n[red]Error: No se pudo conectar al backend. Asegúrate de que FastAPI esté corriendo.[/red]")
    except Exception as e:
        console.print(f"\n[red]Error inesperado al publicar: {e}[/red]")
