from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class RiskCategory(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_ref = Column(String(64), unique=True, index=True, nullable=False)
    customer_id = Column(String(64), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    transaction_type = Column(String(50), nullable=False)   # TRANSFER, PAYMENT, WITHDRAWAL, POS, ONLINE_PURCHASE
    merchant_category = Column(String(50), nullable=False)  # GROCERY, ELECTRONICS, GAMBLING, LUXURY, TRAVEL, CRYPTO, UTILITIES
    payment_channel = Column(String(50), nullable=False)    # MOBILE_APP, NET_BANKING, ATM, POS_TERMINAL, UPI
    country = Column(String(10), default="IN", nullable=False)
    device_id = Column(String(64), nullable=True)
    ip_address = Column(String(64), nullable=True)
    ip_risk_score = Column(Float, default=0.0)
    
    # Behavioral and contextual attributes
    historical_velocity_1h = Column(Integer, default=1)
    historical_amount_avg = Column(Float, default=1000.0)
    distance_from_home_km = Column(Float, default=5.0)
    failed_attempts_count = Column(Integer, default=0)
    
    # Detection outcomes
    is_flagged = Column(Boolean, default=False, index=True)
    risk_score = Column(Integer, default=0, index=True)  # 0 to 100
    risk_category = Column(Enum(RiskCategory), default=RiskCategory.LOW, index=True)
    ml_probability = Column(Float, default=0.0)
    rule_matches = Column(Text, default="[]")  # JSON string
    reasons = Column(Text, default="[]")       # JSON string of explainability factors
    
    # Synthetic ground truth (used for benchmark evaluation only)
    ground_truth_fraud = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship to Alert
    alert = relationship("Alert", back_populates="transaction", uselist=False)
