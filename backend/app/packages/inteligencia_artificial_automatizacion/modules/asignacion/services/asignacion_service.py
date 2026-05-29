"""
Motor de Asignación Inteligente — CU11
Lógica de Ciclo 1:
  1. Buscar talleres ACTIVOS
  2. Asignar prioridad BAJA por defecto (IA: Ciclo 2)
  3. Asignar categoría genérica (IA: Ciclo 2)
  4. Retornar el taller más adecuado (placeholder geofencing)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.packages.gestion_usuarios_seguridad.modules.tenants.repositories.taller_repo import TallerRepository
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.repositories.prioridad_repo import PrioridadRepository
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.repositories.categoria_repo import CategoriaProblemaRepository

async def asignar_taller(db: AsyncSession) -> tuple[str, int, int]:
    """
    Retorna (taller_cod, prioridad_id, categoria_id).
    En Ciclo 1: primer taller ACTIVO / primera prioridad / primera categoría.
    En Ciclo 2 se integrará geofencing e IA.
    """
    # Taller activo
    taller_repo = TallerRepository(db)
    talleres_activos = await taller_repo.get_by_estado("ACTIVO")
    if not talleres_activos:
        raise ValueError("No hay talleres disponibles en este momento.")
    taller = talleres_activos[0]

    # Prioridad por defecto (BAJA)
    prioridad_repo = PrioridadRepository(db)
    prioridades = await prioridad_repo.get_all()
    prioridad = prioridades[0] if prioridades else None

    # Categoría por defecto (Otros)
    categoria_repo = CategoriaProblemaRepository(db)
    categorias = await categoria_repo.get_all()
    categoria = categorias[0] if categorias else None

    return (
        taller.cod,
        prioridad.id if prioridad else 1,
        categoria.id if categoria else 1,
    )
