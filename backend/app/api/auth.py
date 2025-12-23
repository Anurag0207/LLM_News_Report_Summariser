"""Authentication and API key management endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.llm_service import LLMService

router = APIRouter(prefix="/api/auth", tags=["auth"])


class APIKeyRequest(BaseModel):
    provider: str
    api_key: str


class APIKeyResponse(BaseModel):
    valid: bool
    message: str


@router.post("/validate", response_model=APIKeyResponse)
async def validate_api_key(request: APIKeyRequest):
    """Validate an API key for a provider."""
    valid = LLMService.validate_api_key(request.provider, request.api_key)
    
    if valid:
        return APIKeyResponse(valid=True, message="API key is valid")
    else:
        return APIKeyResponse(valid=False, message="API key is invalid or provider is unavailable")

