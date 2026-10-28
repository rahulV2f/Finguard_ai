from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class CaseStatus(str, enum.Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    ESCALATED = "ESCALATED"
    CLOSED_FRAUD = "CLOSED_FRAUD"
    CLOSED_LEGITIMATE = "CLOSED_LEGITIMATE"

class CasePriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class CaseOutcome(str, enum.Enum):
    PENDING = "PENDING"
    FRAUD_CONFIRMED = "FRAUD_CONFIRMED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    INCONCLUSIVE = "INCONCLUSIVE"

class InvestigationCase(Base):
    __tablename__ = "investigation_cases"

    id = Column(Integer, primary_key=True, index=True)
    case_ref = Column(String(64), unique=True, index=True, nullable=False)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False, unique=True)
    
    title = Column(String(255), nullable=False)
    status = Column(Enum(CaseStatus), default=CaseStatus.OPEN, index=True, nullable=False)
    priority = Column(Enum(CasePriority), default=CasePriority.HIGH, nullable=False)
    
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    outcome = Column(Enum(CaseOutcome), default=CaseOutcome.PENDING, nullable=False)
    resolution_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    closed_at = Column(DateTime, nullable=True)

    # Relationships
    alert = relationship("Alert", back_populates="investigation_case")
    assignee = relationship("User", back_populates="assigned_cases", foreign_keys=[assigned_to_id])
    notes = relationship("CaseNote", back_populates="case", cascade="all, delete-orphan", order_by="CaseNote.created_at.asc()")

class CaseNote(Base):
    __tablename__ = "case_notes"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("investigation_cases.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author_name = Column(String(255), nullable=False)
    note = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    case = relationship("InvestigationCase", back_populates="notes")
    author = relationship("User", back_populates="case_notes")
