from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from backend.app.models.transaction import RiskCategory
from backend.app.models.alert import AlertStatus, AlertPriority
from backend.app.schemas.transaction import TransactionResponse
from backend.app.schemas.user import UserResponse

class AlertBase(BaseModel):
    status: AlertStatus
    priority: AlertPriority
    assigned_to_id: Optional[int] = None

class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    priority: Optional[AlertPriority] = None
    assigned_to_id: Optional[int] = None
    notes: Optional[str] = None

class AlertResponse(BaseModel):
    id: int
    alert_ref: str
    transaction_id: int
    risk_score: int
    risk_category: RiskCategory
    detection_method: str
    reasons: str
    status: AlertStatus
    priority: AlertPriority
    assigned_to_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    transaction: Optional[TransactionResponse] = None
    assignee: Optional[UserResponse] = None

    class Config:
        from_attributes = True

class AlertListResponse(BaseModel):
    items: List[AlertResponse]
    total: int
    page: int
    page_size: int
    pages: int
