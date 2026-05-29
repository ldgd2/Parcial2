import os
import argparse
import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
import questionary

console = Console()

COMMANDS = ["dashboard", "test"]

def cprint(rich_msg, plain_msg=""):
    console.print(rich_msg)

def panel_print(rich_content, title="", border="blue"):
    console.print(Panel(rich_content, title=title, border_style=border))

def add_subparsers(subparsers):
    # Dashboard
    parser_dashboard = subparsers.add_parser("dashboard")
    subparsers_dashboard = parser_dashboard.add_subparsers(dest="target")
    subparsers_dashboard.add_parser("view", help="Muestra el resumen financiero del sistema")
    
    # Tests
    parser_test = subparsers.add_parser("test")
    subparsers_test = parser_test.add_subparsers(dest="target")
    subparsers_test.add_parser("ping", help="Revisa si el servidor FastAPI backend esta respondiendo")
    subparsers_test.add_parser("frontend", help="Ejecuta ng test")
    subparsers_test.add_parser("ia", help="Ejecuta el paquete de test de Inteligencia Artificial")
    subparsers_test.add_parser("diag_ai", help="Diagnóstico profundo de cuotas de OpenRouter")
    subparsers_test.add_parser("notifications", help="Test de Notificaciones Push")

def execute(args):
    from .modules.dashboard import dashboard_logic
    from .modules.pruebas import pruebas_logic
    
    if args.category == "dashboard":
        if args.target == "view":
            mostrar_dashboard()
            
    elif args.category == "test":
        if args.target == "ping":
            with console.status("[cyan]Haciendo Healthcheck...[/cyan]"):
                res = pruebas_logic.ping_backend()
                if res["ok"]:
                    panel_print(f"[bold green]Backend Saludable[/bold green]\nEstado: [cyan]{res['status']}[/cyan]\nRespuesta: [white]{res['data']}[/white]", title="Healthcheck API", border="green")
                else:
                    panel_print(f"[bold red][ERROR][/bold red]\n{res['error']}", title="Error", border="red")
        elif args.target == "frontend":
            pruebas_logic.test_frontend()
        elif args.target == "ia":
            pruebas_logic.test_ia()
        elif args.target == "diag_ai":
            pruebas_logic.test_diag_ai()
        elif args.target == "notifications":
            pass # CLI no-interactivo para notificaciones requiere argumentos extra, por simplificidad solo lo exponemos interactivo

def mostrar_dashboard():
    from .modules.dashboard import dashboard_logic
    try:
        stats = asyncio.run(dashboard_logic.get_stats_async())
        
        table = Table(title="[bold magenta]Resumen Financiero - Taller S.O.S.[/bold magenta]", border_style="cyan")
        table.add_column("Concepto", style="bold white")
        table.add_column("Monto / Valor", justify="right")
        
        table.add_row("Ingreso Total Bruto (Clientes)", f"[bold white]${float(stats['total_pagos']):,.2f}[/bold white]")
        table.add_row("Ganancia del Sistema (Comisión 10%)", f"[bold green]${float(stats['total_comision']):,.2f}[/bold green]")
        table.add_row("Total Neto para Talleres", f"[bold cyan]${stats['ganancia_neta']:,.2f}[/bold cyan]")
        table.add_row("Emergencias Finalizadas", f"[bold white]{stats['total_finalizadas']}[/bold white]")
        
        console.print("\n", Align.center(table), "\n")
        
        if stats["taller_stats"]:
            t_table = Table(title="[bold cyan]Desglose de Liquidación por Taller[/bold cyan]", border_style="dim", expand=True)
            t_table.add_column("Nombre del Taller", style="cyan")
            t_table.add_column("Bruto Cobrado", justify="right", style="white")
            t_table.add_column("Comisión Sistema", justify="right", style="green")
            t_table.add_column("Neto para Taller", justify="right", style="bold cyan")
            t_table.add_column("Servicios", justify="center")
            
            for row in stats["taller_stats"]:
                bruto = float(row[1])
                comision = float(row[2])
                neto = bruto - comision
                t_table.add_row(row[0], f"${bruto:,.2f}", f"${comision:,.2f}", f"${neto:,.2f}", str(row[3]))
            
            console.print(Align.center(t_table))
        else:
            console.print(Align.center("[dim]No hay datos de pagos completados registrados aún.[/dim]"))
            
    except Exception as e:
        console.print(f"[bold red]Error al obtener estadísticas:[/bold red] {e}")

def interactuar_notificaciones():
    from .modules.pruebas import pruebas_logic
    tipo = questionary.select(
        "Tipo de Notificación a enviar:",
        choices=["Broadcast (A todos)", "Personalizada (A un Usuario)", "Directa (Por Token)", "Cancelar"]
    ).ask()

    if tipo == "Cancelar" or not tipo: return

    target_token = None
    target_user_id = None
    if tipo == "Directa (Por Token)":
        target_token = questionary.text("Token del dispositivo destino:").ask()
        if not target_token: return
    elif tipo == "Personalizada (A un Usuario)":
        target_user_id = questionary.text("ID del Usuario destino:").ask()
        if not target_user_id: return

    estilo = questionary.select(
        "Estilo/Tipo de Notificación:",
        choices=["Estándar", "Alerta Crítica (Roja)", "Actualización de Estado", "Mensaje de Soporte"]
    ).ask()

    default_title = "TEST NAVAJA SUIZA"
    default_body = "Esta es una prueba desde la estación de control."
    extra_data = {"type": "test"}

    if estilo == "Alerta Crítica (Roja)":
        default_title = "⚠️ ALERTA DE EMERGENCIA"
        default_body = "Se requiere atención inmediata en su ubicación."
        extra_data = {"priority": "high", "color": "red", "type": "emergency"}
    elif estilo == "Actualización de Estado":
        default_title = "✅ Estado Actualizado"
        default_body = "Su vehículo ha sido asignado a un técnico."
        extra_data = {"status": "assigned", "type": "update"}
    elif estilo == "Mensaje de Soporte":
        default_title = "💬 Nuevo Mensaje"
        default_body = "El taller te ha enviado un mensaje."
        extra_data = {"channel": "chat", "type": "message"}

    titulo = questionary.text("Título de la notificación:", default=default_title).ask()
    cuerpo = questionary.text("Cuerpo de la notificación:", default=default_body).ask()

    with console.status("[cyan]Enviando notificación push...[/cyan]"):
        res = pruebas_logic.send_notification_logic(tipo, titulo, cuerpo, extra_data, target_token, target_user_id)
        if res["ok"]:
            panel_print(f"[bold green]Éxito:[/bold green] {res['msg']}", title="Resultado Push", border="green")
        else:
            panel_print(f"[bold red]Error al enviar:[/bold red] {res['error']}", title="Push Failed", border="red")

def interactive_menu():
    from .modules.pruebas import pruebas_logic
    
    while True:
        opt = questionary.select(
            "Categoría QA & Dashboard:",
            choices=["1. Dashboard Financiero", "2. Tests y Pruebas", "Volver"]
        ).ask()
        
        if opt == "Volver" or opt is None:
            break
            
        if "Dashboard" in opt:
            mostrar_dashboard()
        elif "Tests" in opt:
            test_opt = questionary.select(
                "Módulo de Test:",
                choices=[
                    "IA (Whisper/OpenRouter)", 
                    "Diagnóstico de Créditos AI",
                    "Notificaciones Push (Test)",
                    "Ping/Health Backend", 
                    "Frontend (Unit Tests)", 
                    "Volver"
                ]
            ).ask()
            
            if test_opt == "Volver" or test_opt is None: continue
            
            if "IA (Whisper" in test_opt: pruebas_logic.test_ia()
            elif "Diagnóstico" in test_opt: pruebas_logic.test_diag_ai()
            elif "Notificaciones" in test_opt: interactuar_notificaciones()
            elif "Ping" in test_opt: 
                with console.status("[cyan]Haciendo Healthcheck...[/cyan]"):
                    res = pruebas_logic.ping_backend()
                    if res["ok"]:
                        panel_print(f"[bold green]Backend Saludable[/bold green]\nEstado: [cyan]{res['status']}[/cyan]\nRespuesta: [white]{res['data']}[/white]", title="Healthcheck API", border="green")
                    else:
                        panel_print(f"[bold red][ERROR][/bold red]\n{res['error']}", title="Error", border="red")
            else: pruebas_logic.test_frontend()
            
        input("\nPresiona Enter para continuar...")
