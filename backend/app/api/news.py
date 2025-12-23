"""News and text processing endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from ..services.news_service import NewsService

router = APIRouter(prefix="/api/news", tags=["news"])


class ProcessURLsRequest(BaseModel):
    urls: List[str]


class ProcessedURL(BaseModel):
    title: str
    content: str
    url: str
    success: bool
    error: Optional[str] = None


@router.post("/process-urls", response_model=List[ProcessedURL])
async def process_urls(request: ProcessURLsRequest):
    """Process URLs and extract text content."""
    try:
        results = NewsService.process_urls(request.urls)
        return [ProcessedURL(**result) for result in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing URLs: {str(e)}")


class ChunkTextRequest(BaseModel):
    text: str
    chunk_size: int = 1000
    overlap: int = 200


@router.post("/chunk-text", response_model=List[str])
async def chunk_text(request: ChunkTextRequest):
    """Split text into chunks."""
    try:
        chunks = NewsService.chunk_text(
            request.text,
            chunk_size=request.chunk_size,
            overlap=request.overlap
        )
        return chunks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error chunking text: {str(e)}")

