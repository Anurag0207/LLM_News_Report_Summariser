"""Model discovery endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from ..services.llm_service import LLMService

router = APIRouter(prefix="/api/models", tags=["models"])


class ModelListRequest(BaseModel):
    provider: str
    api_key: str


class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    description: str


@router.post("/list", response_model=List[ModelInfo])
async def list_models(request: ModelListRequest):
    """List available models for a provider."""
    try:
        models = LLMService.list_models(request.provider, request.api_key)
        return [ModelInfo(**model) for model in models]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")

