from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from backend.app.models.case import CaseStatus, CasePriority, CaseOutcome
from backend.app.schemas.alert import AlertResponse
from backend.app.schemas.user import UserResponse

class CaseNoteCreate(BaseModel):
    note: str

class CaseNoteResponse(BaseModel):
    id: int
    case_id: int
    user_id: int
    author_name: str
    note: str
    created_at: datetime

    class Config:
        from_attributes = True

class CaseCreate(BaseModel):
    alert_id: int
    title: str
    priority: CasePriority = CasePriority.HIGH
    assigned_to_id: Optional[int] = None

class CaseUpdate(BaseModel):
    status: Optional[CaseStatus] = None
    priority: Optional[CasePriority] = None
    assigned_to_id: Optional[int] = None
    outcome: Optional[CaseOutcome] = None
    resolution_notes: Optional[str] = None

class CaseResponse(BaseModel):
    id: int
    case_ref: str
    alert_id: int
    title: str
    status: CaseStatus
    priority: CasePriority
    assigned_to_id: Optional[int] = None
    outcome: CaseOutcome
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    
    alert: Optional[AlertResponse] = None
    assignee: Optional[UserResponse] = None
    notes: List[CaseNoteResponse] = []

    class Config:
        from_attributes = True

class CaseListResponse(BaseModel):
    items: List[CaseResponse]
    total: int
    page: int
    page_size: int
    pages: int
