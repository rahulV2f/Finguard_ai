import os
from ml_pipeline.train import train_and_evaluate, MODEL_PATH
from backend.app.services.ml_service import ml_service

def test_ml_pipeline_train_and_predict():
    metrics = train_and_evaluate(n_samples=500, random_seed=99)
    assert metrics["precision"] > 0.0
    assert metrics["recall"] > 0.0
    assert metrics["f1_score"] > 0.0
    assert os.path.exists(MODEL_PATH)
    
    ml_service.load_artifacts()
    res = ml_service.predict(
        amount=65000.0,
        currency="INR",
        timestamp=None,
        transaction_type="TRANSFER",
        merchant_category="GAMBLING",
        payment_channel="UPI",
        country="AE",
        ip_risk_score=85.0,
        historical_velocity_1h=5,
        historical_amount_avg=1500.0,
        distance_from_home_km=1200.0,
        failed_attempts_count=3
    )
    assert 0 <= res["risk_score"] <= 100
    assert res["is_flagged"] is True
    assert len(res["reasons"]) > 0

