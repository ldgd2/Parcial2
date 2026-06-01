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
                "2. Variables de Entorno (.env Completo, DB, JWT, APIs)",
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
            
        elif "Variables de Entorno" in category_opt:
            opt = questionary.select(
                "Operación de Config:",
                choices=[
                    "Asistente Completo (Configurar TODO el .env de principio a fin)",
                    "DB (Credenciales PostgreSQL)", 
                    "JWT (Secret Key)", 
                    "Volver"
                ]
            ).ask()
            if opt == "Volver" or opt is None: continue
            
            target = opt.split()[0].lower()
            if target in ("db", "asistente"):
                cprint("\n[bold magenta]--- CONFIGURACION DE BASE DE DATOS ---[/bold magenta]", "\n--- CONFIGURACION DE BASE DE DATOS ---")
                user = questionary.text("Usuario (DB_USER)", default="postgres").ask()
                password = questionary.text("Contrasena (DB_PASSWORD)", default="root").ask()
                host = questionary.text("Host (DB_HOST)", default="localhost").ask()
                port = questionary.text("Puerto (DB_PORT)", default="5432").ask()
                dbname = questionary.text("Nombre DB (DB_NAME)", default="taller_db").ask()
                entornos_logic.config_db(user, password, host, port, dbname)
                cprint(f"[bold green]Configuracion de Base de Datos guardada.[/bold green]", "Configuracion Guardada.")
                
            if target in ("jwt", "asistente"):
                cprint("\n[bold magenta]--- GENERADOR JWT SECRET KEY ---[/bold magenta]", "\n--- GENERADOR JWT SECRET KEY ---")
                genrate = questionary.confirm("Generar una nueva llave segura aleatoria?", default=True).ask()
                if genrate:
                    entornos_logic.config_jwt()
                    cprint(f"[bold green]Nueva llave generada y guardada exitosamente.[/bold green]", "Nueva llave generada exitosamente.")
            
            if target == "asistente":
                cprint("\n[bold magenta]--- CONFIGURACION DE APIS EXTERNAS ---[/bold magenta]", "\n--- CONFIGURACION DE APIS ---")
                openrouter = questionary.text("OpenRouter API Key (OPENROUTER_API_KEY):").ask()
                if openrouter: entornos_logic.update_env_variable(".env", "OPENROUTER_API_KEY", openrouter)
                
                stripe = questionary.text("Stripe Secret Key (STRIPE_SECRET_KEY):").ask()
                if stripe: entornos_logic.update_env_variable(".env", "STRIPE_SECRET_KEY", stripe)
                
                cprint("\n[bold magenta]--- CONFIGURACION DE RED E IP ---[/bold magenta]", "\n--- RED ---")
                local_ip = red_logic.get_local_ip()
                
                current_host = "localhost"
                current_port = "8000"
                if os.path.exists(".env"):
                    try:
                        with open(".env", "r") as f:
                            for line in f:
                                if line.startswith("APP_HOST="): current_host = line.split("=")[1].strip()
                                if line.startswith("APP_PORT_BACKEND="): current_port = line.split("=")[1].strip()
                    except: pass

                host_choice = questionary.select(
                    "¿Qué dirección Host deseas utilizar para el sistema?",
                    choices=[
                        "Local Host (localhost / 127.0.0.1)",
                        f"IP Local de Red ({local_ip})",
                        f"Mantener actual ({current_host})",
                        "Personalizada (Escribir manualmente)"
                    ]
                ).ask()
                
                if host_choice:
                    target_host = "localhost"
                    if "IP Local" in host_choice:
                        target_host = local_ip
                    elif "Mantener" in host_choice:
                        target_host = current_host
                    elif "Personalizada" in host_choice:
                        target_host = questionary.text("Introduce la IP o Host deseado:", default=current_host).ask()
                        
                    target_port = questionary.text("Introduce el puerto del Backend:", default=current_port).ask()
                    
                    red_logic.update_env_variable("APP_HOST", target_host)
                    red_logic.update_env_variable("APP_PORT_BACKEND", target_port)
                    from cli.packages.gestion_servidores_vps.modules.lanzador.lanzador_logic import sync_ip_to_clients
                    sync_ip_to_clients(target_host)
                    cprint(f"[bold green]Red configurada y sincronizada a {target_host}:{target_port}[/bold green]", "Red lista.")
                
                cprint("\n[bold green]¡CONFIGURACIÓN TOTAL DEL .ENV COMPLETADA CON ÉXITO![/bold green]", "Hecho.")
        elif "Red" in category_opt:
            # Leer configuración actual para tener defaults
            from cli.packages.gestion_servidores_vps.modules.lanzador.lanzador_logic import get_app_host, sync_ip_to_clients
            
            opt = questionary.select(
                "Operación de Red:",
                choices=[
                    "Sincronizar (Aplica la IP actual del .env a Angular y Flutter)",
                    "Reconfigurar IP (Cambiar la IP en .env y sincronizar)", 
                    "Volver"
                ]
            ).ask()
            if opt == "Volver" or opt is None: continue
            
            if "Sincronizar" in opt:
                # Extrae el host leyendo .env manualmente o usando la lógica actual
                current_host = "localhost"
                try:
                    if os.path.exists(".env"):
                        with open(".env", 'r') as f:
                            for line in f:
                                if line.startswith("APP_HOST="):
                                    current_host = line.split("=")[1].strip()
                                    break
                except: pass
                sync_ip_to_clients(current_host)
                cprint(f"[bold green]Archivos sincronizados usando la IP del .env: {current_host}[/bold green]", "Red sincronizada.")
                
            elif "Reconfigurar" in opt:
                local_ip = red_logic.get_local_ip()
                
                # Obtener la IP y puerto actual del .env como defaults
                current_host = "localhost"
                current_port = "8000"
                if os.path.exists(".env"):
                    try:
                        with open(".env", "r") as f:
                            for line in f:
                                if line.startswith("APP_HOST="): current_host = line.split("=")[1].strip()
                                if line.startswith("APP_PORT_BACKEND="): current_port = line.split("=")[1].strip()
                    except: pass
                
                host_choice = questionary.select(
                    "¿Qué dirección Host deseas utilizar para el sistema?",
                    choices=[
                        "Local Host (localhost / 127.0.0.1)",
                        f"IP Local de Red ({local_ip})",
                        f"Mantener actual ({current_host})",
                        "Personalizada (Escribir manualmente)"
                    ]
                ).ask()
                
                if not host_choice: continue
                
                target_host = "localhost"
                if "IP Local" in host_choice:
                    target_host = local_ip
                elif "Mantener" in host_choice:
                    target_host = current_host
                elif "Personalizada" in host_choice:
                    target_host = questionary.text("Introduce la IP o Host deseado:", default=current_host).ask()
                    
                target_port = questionary.text("Introduce el puerto del Backend:", default=current_port).ask()
                
                # Actualiza .env
                red_logic.update_env_variable("APP_HOST", target_host)
                red_logic.update_env_variable("APP_PORT_BACKEND", target_port)
                # Sincroniza Angular y Flutter reusando el modulo de lanzador
                sync_ip_to_clients(target_host)
                cprint(f"[bold green]Sincronización y reconfiguración completada con éxito para host: {target_host}:{target_port}[/bold green]", "Red sincronizada.")
            
        input("\nPresiona Enter para continuar...")
