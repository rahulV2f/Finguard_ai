from typing import List, Dict, Any
from pydantic import BaseModel

class DashboardStats(BaseModel):
    total_transactions: int
    flagged_transactions: int
    high_risk_transactions: int
    reviewed_alerts: int
    pending_alerts: int
    total_fraud_loss_prevented: float
    fraud_rate_pct: float
    model_accuracy_pct: float

class VolumeTrendPoint(BaseModel):
    date: str
    total_count: int
    fraud_count: int
    legitimate_count: int
    volume_amount: float

class RiskDistribution(BaseModel):
    category: str
    count: int
    percentage: float
    color: str

class AlertStatusCount(BaseModel):
    status: str
    count: int

class AnalyticsSummary(BaseModel):
    stats: DashboardStats
    daily_volume: List[VolumeTrendPoint]
    risk_distribution: List[RiskDistribution]
    alert_status_breakdown: List[AlertStatusCount]
    channel_breakdown: List[Dict[str, Any]]
    merchant_risk: List[Dict[str, Any]]
