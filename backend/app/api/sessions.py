"""Session management endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..services.session_service import SessionService
from ..models.session import Session as SessionModel, Message as MessageModel

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


class SessionCreate(BaseModel):
    name: str = "New Session"


class SessionResponse(BaseModel):
    id: int
    name: str
    created_at: str
    message_count: int = 0
    
    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    model_used: Optional[str] = None
    created_at: str
    
    model_config = {
        "protected_namespaces": (),
        "from_attributes": True
    }


@router.post("", response_model=SessionResponse)
async def create_session(session_data: SessionCreate, db: Session = Depends(get_db)):
    """Create a new chat session."""
    session = SessionService.create_session(db, session_data.name)
    return SessionResponse(
        id=session.id,
        name=session.name,
        created_at=session.created_at.isoformat(),
        message_count=0
    )


@router.get("", response_model=List[SessionResponse])
async def list_sessions(db: Session = Depends(get_db)):
    """List all sessions."""
    sessions = SessionService.list_sessions(db)
    return [
        SessionResponse(
            id=s.id,
            name=s.name,
            created_at=s.created_at.isoformat(),
            message_count=len(s.messages)
        )
        for s in sessions
    ]


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: int, db: Session = Depends(get_db)):
    """Get a specific session."""
    session = SessionService.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(
        id=session.id,
        name=session.name,
        created_at=session.created_at.isoformat(),
        message_count=len(session.messages)
    )


@router.get("/{session_id}/messages", response_model=List[MessageResponse])
async def get_messages(session_id: int, db: Session = Depends(get_db)):
    """Get all messages for a session."""
    session = SessionService.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = SessionService.get_messages(db, session_id)
    return [
        MessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            model_used=m.model_used,
            created_at=m.created_at.isoformat()
        )
        for m in messages
    ]


@router.delete("/{session_id}")
async def delete_session(session_id: int, db: Session = Depends(get_db)):
    """Delete a session."""
    success = SessionService.delete_session(db, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}


class SessionRename(BaseModel):
    name: str


@router.patch("/{session_id}/rename", response_model=SessionResponse)
async def rename_session(session_id: int, rename_data: SessionRename, db: Session = Depends(get_db)):
    """Rename a session."""
    session = SessionService.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.name = rename_data.name
    db.commit()
    db.refresh(session)
    return SessionResponse(
        id=session.id,
        name=session.name,
        created_at=session.created_at.isoformat(),
        message_count=len(session.messages)
    )


@router.post("/{session_id}/duplicate", response_model=SessionResponse)
async def duplicate_session(session_id: int, db: Session = Depends(get_db)):
    """Duplicate a session with all its messages."""
    original_session = SessionService.get_session(db, session_id)
    if not original_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Create new session
    new_session = SessionService.create_session(db, f"{original_session.name} (Copy)")
    
    # Copy all messages
    messages = SessionService.get_messages(db, session_id)
    for msg in messages:
        SessionService.add_message(
            db=db,
            session_id=new_session.id,
            role=msg.role,
            content=msg.content,
            model_used=msg.model_used
        )
    
    return SessionResponse(
        id=new_session.id,
        name=new_session.name,
        created_at=new_session.created_at.isoformat(),
        message_count=len(messages)
    )

