"""Session management service."""
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.session import Session as SessionModel, Message as MessageModel


class SessionService:
    """Service for managing chat sessions."""
    
    @staticmethod
    def create_session(db: Session, name: str = "New Session") -> SessionModel:
        """Create a new chat session."""
        session = SessionModel(name=name)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def get_session(db: Session, session_id: int) -> Optional[SessionModel]:
        """Get a session by ID."""
        return db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    @staticmethod
    def list_sessions(db: Session, limit: int = 50) -> List[SessionModel]:
        """List all sessions."""
        return db.query(SessionModel).order_by(SessionModel.updated_at.desc()).limit(limit).all()
    
    @staticmethod
    def delete_session(db: Session, session_id: int) -> bool:
        """Delete a session."""
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if session:
            db.delete(session)
            db.commit()
            return True
        return False
    
    @staticmethod
    def add_message(
        db: Session,
        session_id: int,
        role: str,
        content: str,
        model_used: Optional[str] = None
    ) -> MessageModel:
        """Add a message to a session."""
        message = MessageModel(
            session_id=session_id,
            role=role,
            content=content,
            model_used=model_used
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    def get_messages(db: Session, session_id: int) -> List[MessageModel]:
        """Get all messages for a session."""
        return db.query(MessageModel).filter(MessageModel.session_id == session_id).order_by(MessageModel.created_at).all()

