from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AppVersionBase(BaseModel):
    version: str
    changelog: Optional[str] = None
    is_active: Optional[bool] = True

class AppVersionCreate(AppVersionBase):
    file_path: str

class AppVersionOut(AppVersionBase):
    id: int
    file_path: str
    release_date: datetime

    class Config:
        from_attributes = True
