from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.transaction import RiskCategory

class AlertStatus(str, enum.Enum):
    NEW = "NEW"
    UNDER_REVIEW = "UNDER_REVIEW"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    CONFIRMED_FRAUD = "CONFIRMED_FRAUD"
    FALSE_POSITIVE = "FALSE_POSITIVE"

class AlertPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_ref = Column(String(64), unique=True, index=True, nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, unique=True)
    
    risk_score = Column(Integer, nullable=False)
    risk_category = Column(Enum(RiskCategory), nullable=False)
    detection_method = Column(String(50), default="HYBRID_ML_RULES")
    reasons = Column(Text, default="[]")
    
    status = Column(Enum(AlertStatus), default=AlertStatus.NEW, index=True, nullable=False)
    priority = Column(Enum(AlertPriority), default=AlertPriority.HIGH, nullable=False)
    
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    transaction = relationship("Transaction", back_populates="alert")
    assignee = relationship("User", back_populates="assigned_alerts", foreign_keys=[assigned_to_id])
    investigation_case = relationship("InvestigationCase", back_populates="alert", uselist=False)
