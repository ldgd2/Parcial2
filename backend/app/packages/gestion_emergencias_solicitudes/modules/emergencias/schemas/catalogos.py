from pydantic import BaseModel
from typing import Optional

# Base Models
class CatalogoBase(BaseModel):
    descripcion: str

# Especialidad
class EspecialidadBase(BaseModel):
    nombre: str
    descripcion: str

class EspecialidadCreate(EspecialidadBase): pass
class EspecialidadOut(EspecialidadBase):
    id: int
    class Config: from_attributes = True

# Prioridad
class PrioridadCreate(CatalogoBase): pass
class PrioridadOut(CatalogoBase):
    id: int
    class Config: from_attributes = True

# CategoriaProblema
class CategoriaProblemaCreate(CatalogoBase): pass
class CategoriaProblemaOut(CatalogoBase):
    id: int
    class Config: from_attributes = True

# Estado
class EstadoBase(BaseModel):
    nombre: str
    descripcion: str

class EstadoCreate(EstadoBase): pass
class EstadoOut(EstadoBase):
    id: int
    class Config: from_attributes = True
