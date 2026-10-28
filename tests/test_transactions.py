from datetime import datetime, timezone
from backend.app.schemas.transaction import TransactionCreate
from backend.app.services.transaction_service import transaction_service
from backend.app.models.transaction import RiskCategory

def test_transaction_processing_and_scoring(db):
    txn_in = TransactionCreate(
        customer_id="CUST-9999",
        amount=85000.0,
        currency="INR",
        timestamp=datetime.now(timezone.utc),
        transaction_type="TRANSFER",
        merchant_category="CRYPTO",
        payment_channel="NET_BANKING",
        country="IN",
        ip_risk_score=92.0,
        historical_velocity_1h=6,
        historical_amount_avg=1200.0,
        distance_from_home_km=950.0,
        failed_attempts_count=4
    )
    
    txn = transaction_service.process_and_create(db, txn_in)
    assert txn.id is not None
    assert txn.is_flagged is True
    assert txn.risk_score >= 60
    assert txn.risk_category in [RiskCategory.HIGH, RiskCategory.CRITICAL]
    assert txn.alert is not None
    assert txn.alert.risk_score == txn.risk_score

def test_synthetic_data_generation(db):
    txns = transaction_service.generate_synthetic(db, count=15, fraud_ratio=0.20)
    assert len(txns) == 15
    for t in txns:
        assert 0 <= t.risk_score <= 100
        assert t.risk_category in [RiskCategory.LOW, RiskCategory.MEDIUM, RiskCategory.HIGH, RiskCategory.CRITICAL]
