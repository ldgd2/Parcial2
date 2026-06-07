import asyncio
import os
import sys
import importlib.util

# Añadir backend al PYTHONPATH
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "backend"))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.db.session import AsyncSessionLocal

async def run_all_fixes():
    print("=========================================================")
    print("  EJECUCIÓN DE FIXES UNIVERSALES (COLA DE REPARACIÓN)")
    print("=========================================================")
    
    fixes_dir = os.path.dirname(__file__)
    
    # Obtener todos los archivos python en el directorio que empiecen por número
    fix_files = []
    for f in os.listdir(fixes_dir):
        if f.endswith('.py') and f[0].isdigit() and not f.startswith('__'):
            fix_files.append(f)
            
    fix_files.sort() # Ejecutar en orden
    
    if not fix_files:
        print("✅ No hay fixes pendientes en la cola.")
        return
        
    async with AsyncSessionLocal() as db:
        for fix_file in fix_files:
            module_name = fix_file[:-3]
            file_path = os.path.join(fixes_dir, fix_file)
            
            # Cargar el modulo dinamicamente
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'run_fix'):
                try:
                    await module.run_fix(db)
                except Exception as e:
                    print(f"❌ Error al ejecutar el fix {fix_file}: {e}")
                    await db.rollback()
            else:
                print(f"⚠️ El archivo {fix_file} no tiene una función run_fix(db). Omitiendo.")
                
    print("\n=========================================================")
    print("✅ Todos los fixes se han procesado.")
    print("=========================================================")

if __name__ == "__main__":
    asyncio.run(run_all_fixes())
