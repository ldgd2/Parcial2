import os
import subprocess
import platform
import sys

HAS_RICH = False
try:
    from rich.console import Console
    console = Console()
    HAS_RICH = True
except ImportError:
    pass

def cprint(rich_msg, plain_msg):
    if HAS_RICH:
        console.print(rich_msg)
    else:
        print(plain_msg)

def do_status(rich_msg, plain_msg, action_lambda):
    if HAS_RICH:
        with console.status(f"[cyan]{rich_msg}[/cyan]", spinner="dots"):
            action_lambda()
    else:
        print(plain_msg)
        action_lambda()

COMMANDS = ["db"]

def add_subparsers(subparsers):
    parser_db = subparsers.add_parser("db")
    subparsers_db = parser_db.add_subparsers(dest="target")
    subparsers_db.required = True
    
    subparsers_db.add_parser("init", help="Crea todas las tablas directamente (sin Alembic)")
    subparsers_db.add_parser("seed", help="Rellena la base de datos con informacion base")
    
    parser_migrate = subparsers_db.add_parser("migrate", help="Autogenera un script de migracion Alembic")
    parser_migrate.add_argument("-m", "--message", required=True, help="Mensaje para documentar la migracion")
    
    subparsers_db.add_parser("upgrade", help="Aplica las migraciones Alembic pendientes a la Base de Datos")
    subparsers_db.add_parser("sync", help="Autogenera y aplica la migracion en un solo paso")
    subparsers_db.add_parser("stamp", help="Marca la BD con la version actual (Fix si hay desincronizacion)")
    
    # Nuevos comandos del paquete db_tools
    subparsers_db.add_parser("reset", help="[PELIGRO] Destruye el esquema y recrea BD desde Head de Alembic")
    subparsers_db.add_parser("populate", help="Extendido: Siembra proceduralmente la DB usando Faker (N Talleres y M Clientes)")
    subparsers_db.add_parser("diag_serialization", help="Verifica si los datos de la DB se serializan bien a Pydantic")
    subparsers_db.add_parser("fix_specialties", help="Asegura que todos los talleres tengan todas las especialidades (Fix)")
    
    # Seeders
    subparsers_db.add_parser("seeder", help="Crea datos base: estados, prioridades, especialidades, talleres, técnicos y clientes")
    subparsers_db.add_parser("crear-emergencias", help="Crea emergencias consumiendo la API (requiere backend corriendo)")
    subparsers_db.add_parser("crear-emergencias-mock", help="Crea emergencias mapeadas manualmente (sin IA, para pruebas rápidas de Talleres)")
    subparsers_db.add_parser("seed-emergencias", help="Siembra los estados base de emergencias, roles y prioridades (Seed Inicial)")
    
    parser_disable_c = subparsers_db.add_parser("disable-cliente", help="Desactiva logicamente a un cliente por CLI")
    parser_disable_c.add_argument("correo", help="Correo del cliente a desactivar")
    
    parser_disable_t = subparsers_db.add_parser("disable-taller", help="Desactiva logicamente a un taller por CLI")
    parser_disable_t.add_argument("cod", help="Codigo del Taller a desactivar (ej. TAL001)")
    
    subparsers_db.add_parser("add-root-user", help="Crea interactivamente un Super Administrador (Root)")

def execute(args):
    target = args.target

    import time
    python_cmd = sys.executable
    alembic_exe_list = [sys.executable, "-m", "alembic"]

    os.chdir("backend")
    
    try:
        
        if target == "init":
            do_status("Inicializando Base de Datos (SQLAlchemy)...", "Inicializando Base de Datos (SQLAlchemy)...", 
                      lambda: subprocess.run([python_cmd, "../cli/packages/gestion_base_datos/modules/inicializacion/init_db.py"], check=True))
            cprint("[bold green]Base de datos inicializada correctamente.[/bold green]", "Base de datos inicializada correctamente.")
            
        elif target == "seed":
            cprint("[bold red]Seed.py fue eliminado en la refactorización DDD. Usa Populate.[/bold red]", "Usa Populate.")
            
        elif target == "migrate":
            msg = args.message
            do_status(f"Generando archivo de migracion: '{msg}'...", f"Generando archivo de migracion: '{msg}'...", 
                      lambda: subprocess.run([*alembic_exe_list, "revision", "--autogenerate", "-m", msg], check=True))
            cprint("[bold green]Migracion autogenerada exitosamente. Revisa la carpeta backend/alembic/versions.[/bold green]", "Migracion autogenerada exitosamente.")
            
        elif target == "upgrade":
            do_status("Aplicando migraciones estructurales a Head...", "Aplicando migraciones estructurales a Head...", 
                      lambda: subprocess.run([*alembic_exe_list, "upgrade", "head"], check=True))
            cprint("[bold green]Base de datos actualizada a la version Head.[/bold green]", "Base de datos actualizada a la version Head.")

        elif target == "sync":
            msg = f"auto_sync_{int(time.time())}"
            do_status(f"Generando y aplicando cambios estructurales...", "Sincronizando...", 
                      lambda: (subprocess.run([*alembic_exe_list, "revision", "--autogenerate", "-m", msg], check=True), 
                               subprocess.run([*alembic_exe_list, "upgrade", "head"], check=True)))
            cprint(f"[bold green]Base de datos sincronizada con éxito (Migración: {msg})[/bold green]", "BD Sincronizada.")

        elif target == "stamp":
            do_status("Estampando version Head en la BD...", "Estampando...", 
                      lambda: subprocess.run([*alembic_exe_list, "stamp", "head"], check=True))
            cprint("[bold green]BD marcada como actualizada con éxito.[/bold green]", "BD Stamp completado.")
            
        elif target == "fix_heads":
            do_status("Limpiando migraciones locales no oficiales...", "Limpiando...", 
                      lambda: subprocess.run(["git", "clean", "-fd", "alembic/versions/"], check=True))
            cprint("[bold green]Migraciones conflictivas eliminadas. Ahora puedes hacer Upgrade.[/bold green]", "Migraciones conflictivas eliminadas.")

        # ---- Logica conectada a scripts/db_tools ----
        elif target == "reset":
            do_status("Reseteando BD (Drop Cascade)...", "Borrando esquemas...", 
                      lambda: subprocess.run([python_cmd, os.path.join("..", "cli", "packages", "gestion_base_datos", "modules", "db_tools", "reset.py")], check=True))
            cprint("[bold yellow]Iniciando Upgrade asincrono...[/bold yellow]", "Haciendo Upgrade...")
            subprocess.run([*alembic_exe_list, "upgrade", "head"], check=True)
            cprint("[bold green]La base de datos quedo limpia y con migraciones aplicadas.[/bold green]", "La base de ha reseteado a 0 exitosamente.")

        elif target == "populate_exec":
            # --- INYECTAR PYTHONPATH PARA SUBPROCESOS ---
            backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "backend"))
            if "PYTHONPATH" in os.environ:
                os.environ["PYTHONPATH"] = f"{backend_dir}{os.pathsep}{os.environ['PYTHONPATH']}"
            else:
                os.environ["PYTHONPATH"] = backend_dir
            # --------------------------------------------
            cmd = [
                python_cmd, 
                os.path.join("..", "cli", "packages", "gestion_base_datos", "modules", "db_tools", "procedural_seed.py"),
                "--talleres", str(args.talleres),
                "--clientes", str(args.clientes),
                "--emergencias", str(args.emergencias)
            ]
            if args.real_ia:
                cmd.append("--real-ia")
                
            do_status("Generando informacion ficticia + IA Real...", "Sembrando procedimentalmente...", 
                      lambda: subprocess.run(cmd, check=True))
            cprint("[bold green]Poblado Completado con exito.[/bold green]", "Poblado Completado.")

        elif target == "diag_serialization":
            cprint("\n[bold magenta]Iniciando Diagnostico de Datos y Serialización...[/bold magenta]", "\nIniciando Diagnostico...")
            subprocess.run([python_cmd, os.path.join("..", "cli", "packages", "gestion_base_datos", "modules", "diag_db_serialization.py")], check=True)

        elif target == "fix_specialties":
            cprint("\n[bold magenta]Ejecutando Reparación de Especialidades Masiva...[/bold magenta]", "\nEjecutando Reparación...")
            subprocess.run([python_cmd, os.path.join("..", "cli", "packages", "gestion_base_datos", "modules", "tool_fix_specialties.py")], check=True)
            
        elif target == "disable-cliente":
            subprocess.run([python_cmd, "-c", f"import asyncio; import sys; sys.path.append('..'); from cli.packages.gestion_base_datos.modules.db_tools.crud import desactivar_cliente; asyncio.run(desactivar_cliente('{args.correo}'))"])
            
        elif target == "disable-taller":
            subprocess.run([python_cmd, "-c", f"import asyncio; import sys; sys.path.append('..'); from cli.packages.gestion_base_datos.modules.db_tools.crud import desactivar_taller; asyncio.run(desactivar_taller('{args.cod}'))"])

        elif target == "universal-seeder":
            # --- INYECTAR PYTHONPATH PARA SUBPROCESOS ---
            current_dir = os.path.dirname(__file__)
            root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
            backend_dir = os.path.join(root_dir, "backend")
            
            env = os.environ.copy()
            if "PYTHONPATH" in env:
                env["PYTHONPATH"] = f"{backend_dir}{os.pathsep}{root_dir}{os.pathsep}{env['PYTHONPATH']}"
            else:
                env["PYTHONPATH"] = f"{backend_dir}{os.pathsep}{root_dir}"
            # --------------------------------------------
            # WIZARD INTERACTIVO
            # --------------------------------------------
            subprocess.run([python_cmd, "-m", "cli.packages.gestion_base_datos.modules.seeders.wizard"], check=False, cwd=root_dir, env=env)
            
        elif target == "add-root-user":
            subprocess.run([python_cmd, os.path.join("..", "cli", "packages", "gestion_base_datos", "modules", "db_tools", "seed_root.py")])
            
        elif target == "seed-emergencias":
            do_status("Sembrando estados iniciales de emergencias...", "Sembrando estados iniciales...", 
                      lambda: subprocess.run([python_cmd, os.path.join("..", "cli", "packages", "gestion_base_datos", "modules", "db_tools", "seed_emergencias_initial.py")], check=True))
            cprint("[bold green]Seed completado con exito.[/bold green]", "Seed completado.")

            
    except subprocess.CalledProcessError as e:
        cprint(f"\n[bold red][ERROR] Al ejecutar el comando en DB:[/bold red] {e}", f"\n[ERROR] Al ejecutar el comando en DB: {e}")
    finally:
        os.chdir("..")

def interactive_menu():
    """Interfaz interactiva delegada para Base de Datos."""
    import questionary
    import argparse
    
    while True:
        choices = [
            "Init (Tablas iniciales)", 
            "Seeder Universal (Wizard Interactivo)",
            "Agregar Super Usuario Root",
            "Sync (Auto-Migrate + Upgrade)",
            "Upgrade (Aplicar cambios)", 
            "Stamp (Fix Desincronización)",
            "Fix Alembic (Multiple Heads)",
            "Reset (Limpiar y Recrear)", 
            "Populate (Data Falsa)", 
            "Debug Serialización",
            "Fix Especialidades (Talleres)",
            "Seed Emergencias (Estados/Roles)",
            "Volver"
        ]
        opt = questionary.select("Operación de DB:", choices=choices).ask()
    
        if opt == "Volver" or opt is None:
            break
        
        if "Debug Serialización" in opt: target = "diag_serialization"
        elif "Fix Especialidades" in opt: target = "fix_specialties"
        elif "Fix Alembic" in opt: target = "fix_heads"
        elif "Seeder Universal" in opt: target = "universal-seeder"
        elif "Agregar Super Usuario Root" in opt: target = "add-root-user"
        elif "Seed Emergencias" in opt: target = "seed-emergencias"
        else: target = opt.split()[0].lower()
        msg = None
    
        if target == "migrate":
            msg = questionary.text("Mensaje de la migración:").ask()
    
        if target == "populate":
            sub_opt = questionary.select(
                "Tipo de Poblado:",
                choices=[
                    "Básico (Pocos datos)",
                    "Aleatorio (Rango variable)",
                    "Interactivo (Tabla por tabla)",
                    "Solo Emergencias + IA Real",
                    "Poblado Total (Hardcore - IA Masiva)",
                    "Volver"
                ]
            ).ask()
        
            if sub_opt == "Volver" or sub_opt is None: continue
        
            if sub_opt == "Básico (Pocos datos)":
                execute(argparse.Namespace(target="populate_exec", talleres=3, clientes=5, emergencias=0, real_ia=False))
            elif sub_opt == "Aleatorio (Rango variable)":
                import random
                execute(argparse.Namespace(target="populate_exec", talleres=random.randint(1,5), clientes=random.randint(5,15), emergencias=random.randint(1,3), real_ia=True))
            elif sub_opt == "Interactivo (Tabla por tabla)":
                t = int(questionary.text("¿Cuántos Talleres?", default="5").ask() or 5)
                c = int(questionary.text("¿Cuántos Clientes?", default="10").ask() or 10)
                e = int(questionary.text("¿Cuántas Emergencias (+IA)?", default="2").ask() or 2)
                execute(argparse.Namespace(target="populate_exec", talleres=t, clientes=c, emergencias=e, real_ia=True))
            elif sub_opt == "Solo Emergencias + IA Real":
                e = int(questionary.text("¿Cuántas Emergencias a procesar?", default="3").ask() or 3)
                execute(argparse.Namespace(target="populate_exec", talleres=0, clientes=0, emergencias=e, real_ia=True))
            elif sub_opt == "Poblado Total (Hardcore - IA Masiva)":
                execute(argparse.Namespace(target="populate_exec", talleres=5, clientes=15, emergencias=10, real_ia=True))
        else:
            execute(argparse.Namespace(target=target, message=msg))

        input("\nPresiona Enter para continuar...")
