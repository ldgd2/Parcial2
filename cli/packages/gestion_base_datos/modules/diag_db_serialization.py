import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# Setup paths
_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_backend_path = os.path.join(_root_dir, 'backend')
if _backend_path not in sys.path:
    sys.path.insert(0, _backend_path)

load_dotenv(os.path.join(_root_dir, ".env"))

try:
    from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.emergencia import Emergencia
    from app.packages.gestion_emergencias_solicitudes.modules.emergencias.schemas.emergencia import EmergenciaOut
    from app.core._test_mocks import MOCK_CATEGORIAS # Solo por si acaso
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload, joinedload
    from app.db.session import AsyncSessionLocal
    from pydantic import TypeAdapter
except ImportError as e:
    print(f"[ERROR] No se pudo importar los módulos de la aplicación: {e}")
    sys.exit(1)

async def debug_serialization():
    print("Iniciando Verificación de Serialización de Emergencia + IA...")
    async with AsyncSessionLocal() as db:
        # Buscamos la emergencia más reciente para ver si tiene IA
        stmt = (
            select(Emergencia)
            .options(joinedload(Emergencia.resumen_ia))
            .order_by(Emergencia.id.desc())
            .limit(1)
        )
        res = await db.execute(stmt)
        e = res.scalar_one_or_none()
        
        if not e:
            print("[WARN] No se encontraron emergencias en la base de datos.")
            return

        print(f"\n[OK] Emergencia Encontrada: ID {e.id}")
        print(f"   - Descripción: {e.descripcion[:50]}...")
        print(f"   - Tiene Resumen IA: {'SI' if e.resumen_ia else 'NO'}")
        
        if e.resumen_ia:
            print(f"   - Resumen Text: {e.resumen_ia.resumen[:60]}...")
        
        # Probar serialización Pydantic
        print("\nPrueba de Serialización Pydantic (EmergenciaOut):")
        try:
            adapter = TypeAdapter(EmergenciaOut)
            out = adapter.validate_python(e)
            json_data = out.model_dump(mode='json')
            
            print("[OK] Serialización exitosa.")
            if json_data.get('resumen_ia'):
                print("   - resumen_ia en JSON: PRESENTE ✅")
            else:
                print("   - resumen_ia en JSON: AUSENTE ❌")
            
            # Verificación de llaves importantes
            print(f"   - Keys principales: {list(json_data.keys())[:10]}...")
            
        except Exception as ex:
            print(f"[ERROR] Fallo en la serialización Pydantic: {ex}")

if __name__ == "__main__":
    asyncio.run(debug_serialization())
