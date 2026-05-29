import argparse
import sys
import os
import time

# Forzar UTF-8 para arte ASCII en consola de Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# --- Detección de dependencias visuales ---
HAS_RICH = False
HAS_QUESTIONARY = False
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    console = Console()
    HAS_RICH = True
except ImportError:
    pass

try:
    import questionary
    HAS_QUESTIONARY = True
except ImportError:
    pass

# Ensure 'backend' directory is in PYTHONPATH so 'app' imports work
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Propagate PYTHONPATH to any subprocess spawned by the CLI
env_pythonpath = os.environ.get("PYTHONPATH", "")
if backend_path not in env_pythonpath:
    os.environ["PYTHONPATH"] = f"{backend_path}{os.pathsep}{env_pythonpath}" if env_pythonpath else backend_path

from cli.packages.gestion_base_datos import facade as db_facade
from cli.packages.gestion_configuracion import facade as config_facade
from cli.packages.gestion_servidores_vps import facade as server_facade
from cli.packages.pruebas_qa_dashboard import facade as qa_facade

def print_banner():
    banner = """
████████╗ █████╗ ██╗     ██╗     ███████╗██████╗ 
╚══██╔══╝██╔══██╗██║     ██║     ██╔════╝██╔══██╗
   ██║   ███████║██║     ██║     █████╗  ██████╔╝
   ██║   ██╔══██║██║     ██║     ██╔══╝  ██╔══██╗
   ██║   ██║  ██║███████╗███████╗███████╗██║  ██║
   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝
    """
    if HAS_RICH:
        text = Text(banner)
        text.stylize("bold cyan", 0, 100)
        text.stylize("bold magenta", 100, 200)
        text.stylize("bold white", 200, len(banner))
        return text
    else:
        return banner

def get_current_host():
    """Lee el host actual del archivo .env en la raíz."""
    try:
        if os.path.exists(".env"):
            with open(".env", 'r') as f:
                for line in f:
                    if line.startswith("APP_HOST="):
                        return line.split("=")[1].strip()
    except:
        pass
    return "localhost"

def make_dashboard(selected_action="Menu Principal"):
    if not HAS_RICH:
        return "Modo Simple"
        
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=8),
        Layout(name="main", size=15),
        Layout(name="footer", size=3)
    )
    
    layout["header"].update(Align.center(print_banner()))
    
    app_host = get_current_host()
    status_db = "[bold green]ONLINE[/bold green]"
    
    main_panel = Panel(
        Align.center(f"\n[bold green]SISTEMA OPERATIVO[/bold green]\n\n"
                     f"DB Status: {status_db}  |  API Host: [bold cyan]{app_host}[/bold cyan]\n"
                     f"Config File: [dim].env (Root)[/dim]\n"
                     f"Categoría: [bold yellow]{selected_action}[/bold yellow]"),
        title="[bold magenta]Estación de Control AI[/bold magenta]",
        border_style="cyan"
    )
    layout["main"].update(main_panel)
    layout["footer"].update(Panel(Align.center("[italic]Usa las flechas para navegar • 'q' para salir[/italic]"), border_style="dim"))
    
    return layout

def interactive_menu():
    if not HAS_QUESTIONARY or not HAS_RICH:
        print("\n[AVISO] Instalando componentes visuales faltantes...")
        os.system(f"{sys.executable} -m pip install rich questionary")
        os.execv(sys.executable, ['python'] + sys.argv)

    os.system('cls' if os.name == 'nt' else 'clear')
    
    while True:
        console.clear()
        console.print(make_dashboard())
        
        category = questionary.select(
            "Selecciona una categoría de operación:",
            choices=[
                "Lanzar Backend Rápidamente ",
                "Lanzar Frontend Rápidamente ",
                "Lanzar Ambos Rápidamente ",
                "Instalar Dependencias Rápidamente ",
                questionary.Separator(),
                "Base de Datos (SQLAlchemy/Alembic)",
                "Configuración y Entorno (.env, Red, Dependencias)",
                "Servidores y Despliegue (Local, VPS, Git)",
                "Pruebas y Analíticas (QA, IA, Dashboard)",
                "Salir"
            ],
            style=questionary.Style([
                ('qmark', 'fg:#673ab7 bold'),
                ('pointer', 'fg:#ff9800 bold'),
                ('selected', 'fg:#ccddff bold'),
                ('highlighted', 'fg:#00ff00 bold'),
                ('answer', 'fg:#f44336 bold'),
            ])
        ).ask()

        if category == "Salir" or category is None:
            console.print("[bold yellow]Cerrando Navaja Suiza. ¡Hasta pronto![/bold yellow]")
            break

        # Accesos directos
        if "Lanzar Backend" in category:
            from cli.packages.gestion_servidores_vps.modules.lanzador import lanzador_logic
            lanzador_logic.run_backend()
            input("\nPresiona Enter para continuar...")
        elif "Lanzar Frontend" in category:
            from cli.packages.gestion_servidores_vps.modules.lanzador import lanzador_logic
            lanzador_logic.run_frontend()
            input("\nPresiona Enter para continuar...")
        elif "Lanzar Ambos" in category:
            from cli.packages.gestion_servidores_vps.modules.lanzador import lanzador_logic
            lanzador_logic.run_all()
            input("\nPresiona Enter para continuar...")
        elif "Instalar Dependencias" in category:
            from cli.packages.gestion_configuracion.modules.instalacion import instalacion_logic
            instalacion_logic.install_deps()
            input("\nPresiona Enter para continuar...")
        # Delegación modular a Facades
        elif "Base" in category:
            db_facade.menu.interactive_menu()
        elif "Configuración" in category:
            config_facade.menu.interactive_menu()
        elif "Servidores" in category:
            server_facade.menu.interactive_menu()
        elif "Pruebas" in category:
            qa_facade.menu.interactive_menu()

def main():
    if len(sys.argv) > 1 and sys.argv[1] not in ["--help", "-h"]:
        parser = argparse.ArgumentParser(description="Navaja Suiza CLI")
        subparsers = parser.add_subparsers(dest="category")
        
        db_facade.menu.add_subparsers(subparsers)
        config_facade.menu.add_subparsers(subparsers)
        server_facade.menu.add_subparsers(subparsers)
        qa_facade.menu.add_subparsers(subparsers)
        
        args, _ = parser.parse_known_args()
        if args.category:
            # Ejecución directa heredando el contexto a través de las interfaces
            if args.category in db_facade.menu.COMMANDS:
                db_facade.menu.execute(args)
            elif args.category in config_facade.menu.COMMANDS:
                config_facade.menu.execute(args)
            elif args.category in server_facade.menu.COMMANDS:
                server_facade.menu.execute(args)
            elif args.category in qa_facade.menu.COMMANDS:
                qa_facade.menu.execute(args)
            return

    try:
        interactive_menu()
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()
