from typing import Any, Dict, List, Type, TypeVar, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.db.session import Base

ModelType = TypeVar("ModelType", bound="GenericModel")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class GenericModel(Base):
    __abstract__ = True

    @classmethod
    async def get(cls: Type[ModelType], db: AsyncSession, id: Any) -> Union[ModelType, None]:
        """Obtiene un registro por su ID de manera nativa usando el ORM."""
        return await db.get(cls, id)

    @classmethod
    async def get_all(cls: Type[ModelType], db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Obtiene todos los registros con paginación usando ORM."""
        result = await db.execute(select(cls).offset(skip).limit(limit))
        return list(result.scalars().all())

    @classmethod
    async def create(cls: Type[ModelType], db: AsyncSession, *, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        """Crea un nuevo registro usando ORM."""
        obj_in_data = obj_in.model_dump() if isinstance(obj_in, BaseModel) else obj_in
        db_obj = cls(**obj_in_data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(self: ModelType, db: AsyncSession, *, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        """Actualiza la instancia actual con nuevos datos."""
        obj_data = self.__dict__
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        for field in obj_data:
            if field in update_data:
                setattr(self, field, update_data[field])
                
        db.add(self)
        await db.flush()
        await db.refresh(self)
        return self

    @classmethod
    async def remove(cls: Type[ModelType], db: AsyncSession, *, id: Any) -> Union[ModelType, None]:
        """Elimina un registro por su ID usando ORM."""
        obj = await db.get(cls, id)
        if obj:
            await db.delete(obj)
            await db.flush()
        return obj
