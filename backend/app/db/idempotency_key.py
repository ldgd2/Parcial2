from sqlalchemy import Column, String, Integer, JSON, DateTime, func
from sqlalchemy.orm import declarative_base

# No usamos GenericModel porque esto es del sistema core y no necesita tenant-isolation
from app.db.base import Base

class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"
    __table_args__ = {"schema": "public"}

    key = Column(String(36), primary_key=True, index=True)
    method = Column(String(10), nullable=False)
    path = Column(String(500), nullable=False)
    status = Column(String(20), nullable=False, default="processing") # processing | completed | failed
    response_code = Column(Integer, nullable=True)
    response_body = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
