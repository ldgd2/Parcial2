import os
import argparse
from rich.console import Console
import questionary

console = Console()

COMMANDS = ["config", "setup", "network"]

def cprint(rich_msg, plain_msg):
    console.print(rich_msg)

def do_status(rich_msg, plain_msg, action_lambda):
    with console.status(f"[cyan]{rich_msg}[/cyan]", spinner="dots"):
        action_lambda()

def add_subparsers(subparsers):
    # Setup
    parser_setup = subparsers.add_parser("setup")
    subparsers_setup = parser_setup.add_subparsers(dest="target")
    subparsers_setup.add_parser("env", help="Copia .env.example a .env")
    subparsers_setup.add_parser("deps", help="Instala pip install -r requirements.txt")
    subparsers_setup.add_parser("redis", help="Instala y configura Redis via Docker")
    subparsers_setup.add_parser("all", help="Ejecuta env, deps y redis secuencialmente")
    
    # Config
    parser_config = subparsers.add_parser("config")
    subparsers_config = parser_config.add_subparsers(dest="target")
    subparsers_config.add_parser("db", help="Configura interactivamente las credenciales de PostgreSQL")
    subparsers_config.add_parser("jwt", help="Genera dinamicamente un SECRET_KEY seguro para JWT")
    subparsers_config.add_parser("all", help="Configura todo interactivamente")
    
    # Network
    parser_network = subparsers.add_parser("network")
    subparsers_network = parser_network.add_subparsers(dest="target")
    subparsers_network.add_parser("sync", help="Sincroniza la IP/Host en .env y Frontend")

def execute(args):
    # Rutas relativas a los modulos (puramente logicos)
    from .modules.entornos import entornos_logic
    from .modules.instalacion import instalacion_logic
    from .modules.red import red_logic

    if args.category == "setup":
        if args.target in ("env", "all"):
            instalacion_logic.setup_env()
        if args.target in ("deps", "all"):
            instalacion_logic.install_deps()
        if args.target in ("redis", "all"):
            instalacion_logic.setup_redis()
            
    elif args.category == "config":
        if args.target in ("db", "all"):
            entornos_logic.config_db()
        if args.target in ("jwt", "all"):
            entornos_logic.config_jwt()
            
    elif args.category == "network":
        if args.target == "sync":
            red_logic.configure_network_logic("127.0.0.1", "8000") # Desde CLI normal default

def interactive_menu():
    """Unified Interactive Menu for Configuration and Environment"""
    from .modules.entornos import entornos_logic
    from .modules.instalacion import instalacion_logic
    from .modules.red import red_logic
    
    while True:
        category_opt = questionary.select(
            "Categoría de Configuración:",
            choices=[
                "1. Inicialización (.env, Dependencias, Redis)",
                "2. Credenciales y Entorno (DB, JWT)",
                "3. Red y Proxy (Nginx, DNS, Firewall)",
                "Volver"
            ]
        ).ask()
        
        if category_opt == "Volver" or category_opt is None:
            break
            
        if "Inicialización" in category_opt:
            opt = questionary.select(
                "Operación de Instalación:",
                choices=["Env (.env)", "Deps (requirements.txt)", "Redis (Docker)", "All (Todo)", "Volver"]
            ).ask()
            if opt == "Volver" or opt is None: continue
            
            target = opt.split()[0].lower()
            if target in ("env", "all"): instalacion_logic.setup_env()
            if target in ("deps", "all"): instalacion_logic.install_deps()
            if target in ("redis", "all"): instalacion_logic.setup_redis()
            
        elif "Credenciales" in category_opt:
            opt = questionary.select(
                "Operación de Config:",
                choices=["DB (Credenciales PostgreSQL)", "JWT (Secret Key)", "All (Configuración completa)", "Volver"]
            ).ask()
            if opt == "Volver" or opt is None: continue
            
            target = opt.split()[0].lower()
            if target in ("db", "all"):
                cprint("\n[bold magenta]--- CONFIGURACION INDEPENDIENTE DE BASE DE DATOS ---[/bold magenta]", "\n--- CONFIGURACION INDEPENDIENTE DE BASE DE DATOS ---")
                user = questionary.text("Usuario (DB_USER)", default="postgres").ask()
                password = questionary.text("Contrasena (DB_PASSWORD)", default="root").ask()
                host = questionary.text("Host (DB_HOST)", default="localhost").ask()
                port = questionary.text("Puerto (DB_PORT)", default="5432").ask()
                dbname = questionary.text("Nombre DB (DB_NAME)", default="taller_db").ask()
                entornos_logic.config_db(user, password, host, port, dbname)
                cprint(f"[bold green]Configuracion de Base de Datos guardada.[/bold green]", "Configuracion Guardada.")
                
            if target in ("jwt", "all"):
                cprint("\n[bold magenta]--- GENERADOR JWT SECRET KEY ---[/bold magenta]", "\n--- GENERADOR JWT SECRET KEY ---")
                genrate = questionary.confirm("Generar una nueva llave segura aleatoria?", default=True).ask()
                if genrate:
                    entornos_logic.config_jwt()
                    cprint(f"[bold green]Nueva llave generada y guardada exitosamente.[/bold green]", "Nueva llave generada exitosamente.")
            
        elif "Red" in category_opt:
            opt = questionary.select(
                "Operación de Red:",
                choices=["Sync (Sincronizar IP en .env y Frontend)", "Volver"]
            ).ask()
            if opt == "Volver" or opt is None: continue
            
            local_ip = red_logic.get_local_ip()
            host_choice = questionary.select(
                "¿Qué dirección Host deseas utilizar para el sistema?",
                choices=[
                    "Local Host (localhost / 127.0.0.1)",
                    f"IP Local de Red ({local_ip})",
                    "Personalizada (Escribir manualmente)"
                ]
            ).ask()
            
            if not host_choice: continue
            
            target_host = "localhost"
            if "IP Local" in host_choice:
                target_host = local_ip
            elif "Personalizada" in host_choice:
                target_host = questionary.text("Introduce la IP o Host deseado:").ask()
                
            target_port = questionary.text("Introduce el puerto del Backend (default: 8000):", default="8000").ask()
            red_logic.configure_network_logic(target_host, target_port)
            cprint(f"[bold green]Sincronización de red completada con éxito para host: {target_host}:{target_port}[/bold green]", "Red sincronizada.")
            
        input("\nPresiona Enter para continuar...")
