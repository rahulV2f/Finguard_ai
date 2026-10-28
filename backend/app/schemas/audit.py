from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class AuditLogResponse(BaseModel):
    id: int
    event_type: str
    actor_id: Optional[int] = None
    actor_email: str
    entity_type: str
    entity_id: Optional[str] = None
    description: str
    details_json: str
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AuditLogListResponse(BaseModel):
    items: List[AuditLogResponse]
    total: int
    page: int
    page_size: int
    pages: int
