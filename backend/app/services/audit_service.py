import json
from typing import Optional, Any
from sqlalchemy.orm import Session
from backend.app.models.audit import AuditLog
from backend.app.models.user import User

class AuditService:
    @staticmethod
    def log(
        db: Session,
        event_type: str,
        actor: Optional[User],
        entity_type: str,
        description: str,
        entity_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        actor_id = actor.id if actor else None
        actor_email = actor.email if actor else "SYSTEM"
        
        details_str = json.dumps(details or {})
        
        audit_entry = AuditLog(
            event_type=event_type,
            actor_id=actor_id,
            actor_email=actor_email,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            details_json=details_str,
            ip_address=ip_address
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)
        return audit_entry

audit_service = AuditService()
