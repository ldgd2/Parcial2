from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.session import Base

class AppVersion(Base):
    __tablename__ = "app_versions"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), nullable=False, unique=True, index=True)
    file_path = Column(String(255), nullable=False)
    release_date = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    changelog = Column(String(500), nullable=True)
