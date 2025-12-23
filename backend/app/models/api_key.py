"""API key storage model."""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..database import Base


class APIKey(Base):
    """API key storage model (encrypted in production)."""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False, index=True)  # 'openai', 'gemini', 'openrouter'
    key_hash = Column(String, nullable=False)  # In production, use proper encryption
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Integer, default=1)  # 1 for active, 0 for inactive

