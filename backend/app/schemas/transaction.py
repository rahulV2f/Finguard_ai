from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from backend.app.models.transaction import RiskCategory

class TransactionBase(BaseModel):
    customer_id: str
    amount: float = Field(..., gt=0)
    currency: str = "INR"
    timestamp: Optional[datetime] = None
    transaction_type: str = "PAYMENT"
    merchant_category: str = "RETAIL"
    payment_channel: str = "MOBILE_APP"
    country: str = "IN"
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    ip_risk_score: float = 0.0
    historical_velocity_1h: int = 1
    historical_amount_avg: float = 1000.0
    distance_from_home_km: float = 5.0
    failed_attempts_count: int = 0

class TransactionCreate(TransactionBase):
    transaction_ref: Optional[str] = None

class RiskExplanation(BaseModel):
    factor: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    weight: float

class PredictionResponse(BaseModel):
    risk_score: int  # 0 to 100
    risk_category: RiskCategory
    ml_probability: float
    is_flagged: bool
    detection_method: str
    rule_matches: List[str]
    reasons: List[RiskExplanation]

class TransactionResponse(TransactionBase):
    id: int
    transaction_ref: str
    timestamp: datetime
    is_flagged: bool
    risk_score: int
    risk_category: RiskCategory
    ml_probability: float
    rule_matches: str
    reasons: str
    created_at: datetime

    class Config:
        from_attributes = True

class TransactionListResponse(BaseModel):
    items: List[TransactionResponse]
    total: int
    page: int
    page_size: int
    pages: int

class SyntheticGenerateRequest(BaseModel):
    count: int = Field(default=50, ge=1, le=500)
    fraud_ratio: float = Field(default=0.15, ge=0.0, le=1.0)
