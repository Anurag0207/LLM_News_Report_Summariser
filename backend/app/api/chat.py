"""Chat and text generation endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import json
import logging
from ..database import get_db
from ..services.llm_service import LLMService
from ..services.session_service import SessionService

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    provider: str
    api_key: str
    model: str
    prompt: str
    session_id: Optional[int] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    enable_search: bool = True
    search_api_key: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    model_used: str
    session_id: Optional[int] = None
    
    model_config = {"protected_namespaces": ()}


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Generate a chat response (non-streaming)."""
    try:
        # Generate response
        response_text = LLMService.generate_text(
            provider=request.provider,
            api_key=request.api_key,
            prompt=request.prompt,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            enable_search=request.enable_search,
            search_api_key=request.search_api_key
        )
        
        # Save to session if provided
        session_id = request.session_id
        if session_id:
            # Verify session exists
            session = SessionService.get_session(db, session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            # Save user message
            SessionService.add_message(
                db=db,
                session_id=session_id,
                role="user",
                content=request.prompt,
                model_used=None
            )
            
            # Save assistant response
            SessionService.add_message(
                db=db,
                session_id=session_id,
                role="assistant",
                content=response_text,
                model_used=request.model
            )
        
        return ChatResponse(
            response=response_text,
            model_used=request.model,
            session_id=session_id
        )
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")


@router.post("/stream")
async def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    """Generate a streaming chat response using Server-Sent Events."""
    async def generate():
        full_response = ""
        try:
            # Save user message first if session provided
            session_id = request.session_id
            if session_id:
                session = SessionService.get_session(db, session_id)
                if not session:
                    yield f"data: {json.dumps({'type': 'error', 'content': 'Session not found'})}\n\n"
                    return
                
                SessionService.add_message(
                    db=db,
                    session_id=session_id,
                    role="user",
                    content=request.prompt,
                    model_used=None
                )
            
            # Stream response
            chunk_count = 0
            async for chunk_data in LLMService.generate_stream(
                provider=request.provider,
                api_key=request.api_key,
                prompt=request.prompt,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                enable_search=request.enable_search,
                search_api_key=request.search_api_key
            ):
                chunk_count += 1
                # Handle both string chunks (from adapters) and dict chunks (for special events)
                if isinstance(chunk_data, str):
                    # Adapters yield strings directly
                    chunk_content = chunk_data
                    chunk_type = "text"
                elif isinstance(chunk_data, dict):
                    # Handle dictionary chunks for special events
                    chunk_type = chunk_data.get("type", "text")
                    chunk_content = chunk_data.get("content", "")
                else:
                    # Fallback: convert to string
                    chunk_content = str(chunk_data) if chunk_data is not None else ""
                    chunk_type = "text"
                
                # Ensure chunk_content is a string, not None
                if chunk_content is None:
                    chunk_content = ""
                
                # Skip empty chunks to avoid sending unnecessary data
                if not chunk_content and chunk_type == "text":
                    continue
                
                logger.debug(f"Yielding chunk {chunk_count}: type={chunk_type}, content_length={len(chunk_content)}")
                
                if chunk_type == "text":
                    full_response += chunk_content
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk_content})}\n\n"
                elif chunk_type == "search_results":
                    yield f"data: {json.dumps({'type': 'search_results', 'content': chunk_content})}\n\n"
                elif chunk_type == "tool_call":
                    yield f"data: {json.dumps({'type': 'tool_call', 'content': chunk_content})}\n\n"
            
            logger.info(f"Stream completed: {chunk_count} chunks processed, {len(full_response)} total characters")
            
            # Save complete response to session
            if session_id:
                SessionService.add_message(
                    db=db,
                    session_id=session_id,
                    role="assistant",
                    content=full_response,
                    model_used=request.model
                )
            
            # Send final event
            yield f"data: {json.dumps({'type': 'done', 'content': full_response})}\n\n"
            
        except Exception as e:
            error_msg = f"Error in streaming: {str(e)}"
            logger.error(error_msg, exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
