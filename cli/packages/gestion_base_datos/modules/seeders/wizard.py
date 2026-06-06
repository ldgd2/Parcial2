import os
import sys
import asyncio
import questionary

from .seed_planes_roles import seed_planes_y_roles
from .seed_especialidades import seed_especialidades_mecanicas
from .seed_talleres import seed_nuevo_taller
from .seed_clientes import seed_nuevo_cliente
from .seed_emergencias import seed_emergencias_inteligentes
from .seed_cotizaciones import seed_cotizaciones

async def interactive_wizard():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=========================================================")
    print("   S E E D E R   U N I V E R S A L   ( W I Z A R D )")
    print("=========================================================")
    print("Sistema de poblado interactivo. Respeta la integridad relacional.\n")
    
    while True:
        choice = await questionary.select(
            "¿Qué entidad deseas sembrar/crear?",
            choices=[
                "1. Planes de Suscripción y Roles (Base del sistema)",
                "2. Especialidades Mecánicas",
                "3. Clientes",
                "4. Talleres (Requiere Planes)",
                "5. Emergencias Inteligentes (Requiere Clientes y Talleres)",
                "6. Cotizaciones (Requiere Emergencias)",
                "7. Script Seeder Legacy Completo (Poblar TODO automáticamente)",
                "8. Generador Procedural (Faker) Automático",
                questionary.Separator(),
                "Volver al menú principal"
            ],
            style=questionary.Style([
                ('qmark', 'fg:#673ab7 bold'),
                ('pointer', 'fg:#ff9800 bold'),
                ('selected', 'fg:#ccddff bold'),
            ])
        ).ask_async()
        
        if not choice or choice == "Volver al menú principal":
            break
            
        try:
            if choice.startswith("1"):
                await seed_planes_y_roles()
            elif choice.startswith("2"):
                await seed_especialidades_mecanicas()
            elif choice.startswith("3"):
                await seed_nuevo_cliente()
            elif choice.startswith("4"):
                await seed_nuevo_taller()
            elif choice.startswith("5"):
                await seed_emergencias_inteligentes()
            elif choice.startswith("6"):
                await seed_cotizaciones()
            elif choice.startswith("7"):
                from .seeder import seed_database
                await seed_database()
            elif choice.startswith("8"):
                from .seed_procedural_faker import run_procedural_seeder
                await run_procedural_seeder()
        except Exception as e:
            print(f"\n❌ Error durante la ejecución del seeder: {e}")
            
        input("\nPresiona Enter para continuar...")
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    asyncio.run(interactive_wizard())
