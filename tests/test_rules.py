from backend.app.services.rule_engine import rule_engine

def test_rule_velocity_spike():
    res = rule_engine.evaluate(
        amount=500.0,
        historical_avg=1000.0,
        velocity_1h=7,
        distance_km=2.0,
        failed_attempts=0,
        ip_risk=10.0,
        merchant_cat="GROCERY",
        hour_of_day=14,
        is_cross_border=False
    )
    assert "RULE_VELOCITY_SPIKE_5_IN_1H" in res["matched_rules"]
    assert res["rule_score"] >= 30

def test_rule_amount_spike():
    res = rule_engine.evaluate(
        amount=50000.0,
        historical_avg=1000.0,
        velocity_1h=1,
        distance_km=2.0,
        failed_attempts=0,
        ip_risk=10.0,
        merchant_cat="RETAIL",
        hour_of_day=14,
        is_cross_border=False
    )
    assert "RULE_AMOUNT_10X_HISTORICAL_AVG" in res["matched_rules"]
    assert res["rule_score"] >= 35

def test_rule_impossible_travel():
    res = rule_engine.evaluate(
        amount=1000.0,
        historical_avg=1000.0,
        velocity_1h=1,
        distance_km=1800.0,
        failed_attempts=0,
        ip_risk=20.0,
        merchant_cat="ELECTRONICS",
        hour_of_day=14,
        is_cross_border=True
    )
    assert "RULE_IMPOSSIBLE_TRAVEL_DISTANCE" in res["matched_rules"]
    assert "RULE_CROSS_BORDER_FOREIGN_TRANSACTION" in res["matched_rules"]
