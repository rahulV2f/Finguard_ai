from typing import Dict, Any, List

def generate_risk_explanations(
    amount: float,
    hist_avg: float,
    velocity: int,
    distance_km: float,
    failed_attempts: int,
    ip_risk: float,
    merchant_cat: str,
    hour_of_day: int,
    is_cross_border: bool,
    ml_prob: float
) -> List[Dict[str, Any]]:
    reasons = []
    
    # 1. Amount deviation
    ratio = amount / max(1.0, hist_avg)
    if ratio >= 10.0:
        reasons.append({
            "factor": "EXTREME_AMOUNT_SPIKE",
            "severity": "CRITICAL",
            "description": f"Transaction amount of ₹{amount:,.2f} is {ratio:.1f}x higher than customer's 30-day baseline of ₹{hist_avg:,.2f}.",
            "weight": 0.35
        })
    elif ratio >= 3.5:
        reasons.append({
            "factor": "UNUSUAL_AMOUNT_ANOMALY",
            "severity": "HIGH",
            "description": f"Transaction amount of ₹{amount:,.2f} significantly exceeds historical average (₹{hist_avg:,.2f}).",
            "weight": 0.20
        })
        
    # 2. Velocity spike
    if velocity >= 6:
        reasons.append({
            "factor": "VELOCITY_BURST",
            "severity": "CRITICAL",
            "description": f"High frequency: {velocity} transactions initiated in the past 60 minutes, indicating potential carding or automated exploitation.",
            "weight": 0.25
        })
    elif velocity >= 3:
        reasons.append({
            "factor": "MODERATE_VELOCITY",
            "severity": "MEDIUM",
            "description": f"{velocity} transactions within one hour deviates from standard customer cadence.",
            "weight": 0.12
        })
        
    # 3. Impossible travel / Geographic deviation
    if distance_km >= 800:
        reasons.append({
            "factor": "GEOGRAPHIC_IMPOSSIBILITY",
            "severity": "CRITICAL",
            "description": f"Transaction originated {distance_km:,.1f} km from primary registered address within a window inconsistent with physical travel.",
            "weight": 0.25
        })
    elif is_cross_border:
        reasons.append({
            "factor": "CROSS_BORDER_DESTINATION",
            "severity": "HIGH",
            "description": "Foreign foreign-exchange settlement detected for domestic-only retail profile.",
            "weight": 0.18
        })
        
    # 4. Off-hour / Midnight burst
    if 1 <= hour_of_day <= 5:
        reasons.append({
            "factor": "UNUSUAL_OFF_PEAK_TIME",
            "severity": "MEDIUM",
            "description": f"Transaction submitted at {hour_of_day:02d}:00 hours (midnight window), anomalous for this account.",
            "weight": 0.15
        })
        
    # 5. Failed security attempts
    if failed_attempts >= 3:
        reasons.append({
            "factor": "MULTIPLE_FAILED_AUTH",
            "severity": "HIGH",
            "description": f"{failed_attempts} failed PIN/OTP attempts recorded immediately prior to successful execution.",
            "weight": 0.20
        })
        
    # 6. IP risk / Proxy / Emulator
    if ip_risk >= 75.0:
        reasons.append({
            "factor": "HIGH_RISK_NETWORK_IP",
            "severity": "HIGH",
            "description": f"Connecting IP risk score is {ip_risk:.1f}/100 with indicators of VPN/datacenter/TOR proxy usage.",
            "weight": 0.18
        })
        
    # 7. High-risk merchant category
    if merchant_cat in ["GAMBLING", "CRYPTO"]:
        reasons.append({
            "factor": "HIGH_RISK_MERCHANT",
            "severity": "HIGH",
            "description": f"Merchant category classified as {merchant_cat}, subject to strict anti-money laundering thresholds.",
            "weight": 0.15
        })
        
    # If no reasons were triggered but ML probability is elevated
    if not reasons and ml_prob >= 0.5:
        reasons.append({
            "factor": "ML_ENSEMBLE_PATTERN",
            "severity": "MEDIUM",
            "description": "Composite multi-feature interaction flagged by Random Forest model as exhibiting subtle fraud pattern.",
            "weight": 0.20
        })
        
    return reasons
