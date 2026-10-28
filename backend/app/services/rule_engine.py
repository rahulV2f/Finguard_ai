from typing import List, Dict, Any

class RuleEngine:
    """
    Transparent Rule-Based Baseline Engine for Banking Fraud Detection.
    Rules act as deterministic guards that complement statistical ML models.
    """
    
    @staticmethod
    def evaluate(
        amount: float,
        historical_avg: float,
        velocity_1h: int,
        distance_km: float,
        failed_attempts: int,
        ip_risk: float,
        merchant_cat: str,
        hour_of_day: int,
        is_cross_border: bool
    ) -> Dict[str, Any]:
        matched_rules = []
        rule_score = 0
        
        # Rule 1: High Velocity Spike
        if velocity_1h >= 5:
            matched_rules.append("RULE_VELOCITY_SPIKE_5_IN_1H")
            rule_score += 30
        elif velocity_1h >= 3:
            matched_rules.append("RULE_ELEVATED_VELOCITY_3_IN_1H")
            rule_score += 15
            
        # Rule 2: Amount Exceeds 8x Historical Baseline
        ratio = amount / max(1.0, historical_avg)
        if ratio >= 10.0:
            matched_rules.append("RULE_AMOUNT_10X_HISTORICAL_AVG")
            rule_score += 35
        elif ratio >= 4.0:
            matched_rules.append("RULE_AMOUNT_4X_HISTORICAL_AVG")
            rule_score += 20
            
        # Rule 3: Geographic Impossible Travel (> 800km)
        if distance_km >= 800:
            matched_rules.append("RULE_IMPOSSIBLE_TRAVEL_DISTANCE")
            rule_score += 25
            
        # Rule 4: Cross-Border Foreign Currency
        if is_cross_border:
            matched_rules.append("RULE_CROSS_BORDER_FOREIGN_TRANSACTION")
            rule_score += 15
            
        # Rule 5: Repeated Failed Attempts (Brute Force Indicator)
        if failed_attempts >= 3:
            matched_rules.append("RULE_EXCESSIVE_FAILED_ATTEMPTS")
            rule_score += 25
            
        # Rule 6: High Risk IP Proxy / VPN Indicator
        if ip_risk >= 80.0:
            matched_rules.append("RULE_HIGH_RISK_IP_SCORE")
            rule_score += 20
            
        # Rule 7: Midnight Off-Hour Transaction
        if 1 <= hour_of_day <= 4 and amount > 5000:
            matched_rules.append("RULE_LATE_NIGHT_HIGH_VALUE")
            rule_score += 15
            
        # Rule 8: High Risk Category
        if merchant_cat in ["GAMBLING", "CRYPTO"]:
            matched_rules.append(f"RULE_HIGH_RISK_MERCHANT_{merchant_cat}")
            rule_score += 15

        capped_rule_score = min(100, rule_score)
        return {
            "matched_rules": matched_rules,
            "rule_score": capped_rule_score,
            "has_rule_trigger": len(matched_rules) > 0
        }

rule_engine = RuleEngine()
