import os
import argparse
from rich.console import Console
from rich.panel import Panel
import questionary

console = Console()

COMMANDS = ["run", "deploy", "vps"]

def cprint(rich_msg, plain_msg=""):
    console.print(rich_msg)

def panel_print(rich_content, border="blue"):
    console.print(Panel(rich_content, border_style=border))

def add_subparsers(subparsers):
    # Run
    parser_run = subparsers.add_parser("run")
    subparsers_run = parser_run.add_subparsers(dest="target")
    subparsers_run.add_parser("backend", help="Abre Uvicorn en modo desarrollo (FastAPI)")
    subparsers_run.add_parser("frontend", help="Abre ng serve en modo desarrollo (Angular)")
    subparsers_run.add_parser("all", help="Inicia ambos servidores simultaneamente")
    
    # Deploy
    parser_deploy = subparsers.add_parser("deploy")
    parser_deploy.add_argument("--domain", help="Dominio o IP del servidor")
    parser_deploy.add_argument("--port-backend", type=int, default=8000, help="Puerto para el backend")
    parser_deploy.add_argument("--port-frontend", type=int, default=80, help="Puerto para el frontend")
    
    # VPS
    parser_vps = subparsers.add_parser("vps")
    subparsers_vps = parser_vps.add_subparsers(dest="target")
    subparsers_vps.add_parser("setup", help="Crea Servicios Systemd (Backend/Frontend)")
    subparsers_vps.add_parser("check", help="Verifica Estado de Servicios (Solo Linux)")
    subparsers_vps.add_parser("restart", help="Reinicia Todos los Servicios (Solo Linux)")
    subparsers_vps.add_parser("delete", help="Elimina Servicios Systemd (Solo Linux)")

def execute(args):
    from .modules.lanzador import lanzador_logic
    from .modules.despliegue import despliegue_logic
    from .modules.vps import vps_logic

    if args.category == "run":
        if args.target == "backend": lanzador_logic.run_backend()
        elif args.target == "frontend": lanzador_logic.run_frontend()
        elif args.target == "all": lanzador_logic.run_all()
            
    elif args.category == "deploy":
        domain = args.domain or despliegue_logic.get_public_ip()
        despliegue_logic.execute_logic(domain, args.port_backend, args.port_frontend)
        
    elif args.category == "vps":
        if args.target == "setup": vps_logic.setup_vps_services("8000", "4200") # defaults
        elif args.target == "check": vps_logic.check_services()
        elif args.target == "restart": vps_logic.restart_services()
        elif args.target == "delete": vps_logic.delete_services()

def interactive_menu():
    from .modules.lanzador import lanzador_logic
    from .modules.despliegue import despliegue_logic
    from .modules.vps import vps_logic
    
    while True:
        category_opt = questionary.select(
            "Módulo de Servidores:",
            choices=[
                "1. Lanzador Local (Dev)",
                "2. Despliegue Producción (Nginx)",
                "3. Gestión VPS (Daemons/Systemd)",
                "Volver"
            ]
        ).ask()
        
        if category_opt == "Volver" or category_opt is None:
            break
            
        if "Lanzador" in category_opt:
            opt = questionary.select(
                "Iniciar Servidor:",
                choices=["Backend (FastAPI)", "Frontend (Angular)", "Ambos (Concurrente)", "Volver"]
            ).ask()
            if opt == "Volver" or opt is None: continue
            
            target = opt.split()[0].lower()
            if target == "backend": lanzador_logic.run_backend()
            elif target == "frontend": lanzador_logic.run_frontend()
            elif target == "ambos": lanzador_logic.run_all()
            
        elif "Despliegue" in category_opt:
            public_ip = despliegue_logic.get_public_ip()
            cprint(f"[dim]IP Detectada automáticamente:[/dim] [bold green]{public_ip}[/bold green]")

            port_backend = questionary.text("¿En qué puerto quieres correr el BACKEND?", default="8000").ask()
            port_frontend = questionary.text("¿En qué puerto quieres correr el FRONTEND (Nginx)?", default="80").ask()
            domain = questionary.text("¿Dominio o IP para el servidor? (Enter para usar la IP detectada)", default=public_ip).ask()

            despliegue_logic.execute_logic(domain, int(port_backend), int(port_frontend))
            
        elif "VPS" in category_opt:
            choice = questionary.select(
                "¿Qué acción deseas realizar en el VPS?",
                choices=[
                    "Crear Servicios Systemd (Backend/Frontend)",
                    "Verificar Estado de Servicios (Solo Linux)",
                    "Reiniciar Todos los Servicios (Solo Linux)",
                    "Eliminar Servicios Systemd (Solo Linux)",
                    "Ver Logs Backend",
                    "Ver Logs Frontend",
                    "Editar IP y Puertos (.env + Sync)",
                    "Volver"
                ]
            ).ask()
            if choice == "Volver" or choice is None: continue
            
            if "Crear" in choice:
                public_ip = vps_logic.get_public_ip()
                port_back = questionary.text("Puerto para el servicio BACKEND (FastAPI):", default="8000").ask()
                port_front = questionary.text("Puerto para el servicio FRONTEND (Angular DEV):", default="4200").ask()
                
                vps_logic.setup_vps_services(port_back, port_front)
                
                install = questionary.confirm("¿Deseas instalar y activar estos servicios de ejecución ahora mismo?").ask()
                if install:
                    vps_logic.install_services(public_ip, port_back, port_front)
                    
            elif "Verificar" in choice: vps_logic.check_services()
            elif "Reiniciar" in choice: vps_logic.restart_services()
            elif "Eliminar" in choice:
                confirm = questionary.confirm("¿Estás seguro de detener y eliminar los servicios?").ask()
                if confirm: vps_logic.delete_services()
            elif "Logs Backend" in choice: vps_logic.view_logs("backend")
            elif "Logs Frontend" in choice: vps_logic.view_logs("frontend")
            elif "Editar" in choice:
                port_back = questionary.text("Nuevo puerto para BACKEND:", default="8000").ask()
                vps_logic.edit_network_config(port_back)
                
        input("\nPresiona Enter para continuar...")
