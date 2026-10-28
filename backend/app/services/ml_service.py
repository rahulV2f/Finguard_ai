import os
import json
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List
from backend.app.core.config import settings
from backend.app.models.transaction import RiskCategory
from backend.app.services.rule_engine import rule_engine
from ml_pipeline.explainability import generate_risk_explanations

class MLService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.metrics = None
        self.model_path = os.path.join(settings.MODEL_DIR, "finguard_rf_model.joblib")
        self.scaler_path = os.path.join(settings.MODEL_DIR, "finguard_scaler.joblib")
        self.metrics_path = os.path.join(settings.MODEL_DIR, "metrics.json")
        self.load_artifacts()

    def load_artifacts(self):
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                if os.path.exists(self.metrics_path):
                    with open(self.metrics_path, "r") as f:
                        self.metrics = json.load(f)
                print("FinGuard ML models and scalers loaded successfully.")
            else:
                print("ML model files not found yet; will train or use rule baseline.")
        except Exception as e:
            print(f"Warning: Could not load ML artifacts: {e}")

    def predict(
        self,
        amount: float,
        currency: str,
        timestamp,
        transaction_type: str,
        merchant_category: str,
        payment_channel: str,
        country: str,
        ip_risk_score: float,
        historical_velocity_1h: int,
        historical_amount_avg: float,
        distance_from_home_km: float,
        failed_attempts_count: int
    ) -> Dict[str, Any]:
        hour = timestamp.hour if hasattr(timestamp, "hour") else 12
        is_cross_border = (country != "IN")

        # 1. Evaluate Rule Engine Baseline
        rule_eval = rule_engine.evaluate(
            amount=amount,
            historical_avg=historical_amount_avg,
            velocity_1h=historical_velocity_1h,
            distance_km=distance_from_home_km,
            failed_attempts=failed_attempts_count,
            ip_risk=ip_risk_score,
            merchant_cat=merchant_category,
            hour_of_day=hour,
            is_cross_border=is_cross_border
        )
        rule_score = rule_eval["rule_score"]
        matched_rules = rule_eval["matched_rules"]

        # 2. Evaluate ML Model Probability
        ml_probability = 0.0
        if self.model is not None and self.scaler is not None:
            try:
                # Prepare feature vector matching training schema
                high_risk_merchants = {"GAMBLING": 1.0, "CRYPTO": 1.0, "LUXURY": 0.7, "ELECTRONICS": 0.5, "TRAVEL": 0.4}
                channel_risk = {"UPI": 0.6, "MOBILE_APP": 0.4, "NET_BANKING": 0.5, "ATM": 0.3, "POS_TERMINAL": 0.2}
                
                ratio = amount / max(1.0, historical_amount_avg)
                is_night = 1.0 if (1 <= hour <= 5) else 0.0
                day_of_week = timestamp.weekday() if hasattr(timestamp, "weekday") else 0
                is_weekend = 1.0 if day_of_week >= 5 else 0.0
                m_weight = high_risk_merchants.get(merchant_category, 0.1)
                c_weight = channel_risk.get(payment_channel, 0.2)
                cb_float = 1.0 if is_cross_border else 0.0

                features = np.array([[
                    float(amount),
                    float(historical_amount_avg),
                    float(ratio),
                    float(historical_velocity_1h),
                    float(distance_from_home_km),
                    float(failed_attempts_count),
                    float(ip_risk_score),
                    float(hour),
                    float(is_night),
                    float(is_weekend),
                    float(m_weight),
                    float(c_weight),
                    float(cb_float)
                ]])
                
                scaled_features = self.scaler.transform(features)
                probs = self.model.predict_proba(scaled_features)[0]
                ml_probability = float(probs[1])
            except Exception as e:
                print(f"Inference warning, using rule score: {e}")
                ml_probability = rule_score / 100.0
        else:
            ml_probability = rule_score / 100.0

        # 3. Hybrid Risk Score Blend (65% ML Model probability + 35% deterministic rule weight)
        ml_score = int(round(ml_probability * 100))
        final_risk_score = int(round((ml_score * 0.65) + (rule_score * 0.35)))
        # Ensure any hard critical rule violations guarantee minimum 65 score
        if len(matched_rules) >= 2 and final_risk_score < 65:
            final_risk_score = 65
        final_risk_score = max(0, min(100, final_risk_score))

        # 4. Determine Risk Category Band
        if final_risk_score <= settings.RISK_LOW_MAX:
            category = RiskCategory.LOW
        elif final_risk_score <= settings.RISK_MEDIUM_MAX:
            category = RiskCategory.MEDIUM
        elif final_risk_score <= settings.RISK_HIGH_MAX:
            category = RiskCategory.HIGH
        else:
            category = RiskCategory.CRITICAL

        is_flagged = (final_risk_score >= settings.ALERT_TRIGGER_THRESHOLD) or (len(matched_rules) > 0)

        # 5. Explainability factors
        reasons = generate_risk_explanations(
            amount=amount,
            hist_avg=historical_amount_avg,
            velocity=historical_velocity_1h,
            distance_km=distance_from_home_km,
            failed_attempts=failed_attempts_count,
            ip_risk=ip_risk_score,
            merchant_cat=merchant_category,
            hour_of_day=hour,
            is_cross_border=is_cross_border,
            ml_prob=ml_probability
        )

        detection_method = "HYBRID_ML_RULES" if self.model else "RULE_BASED_BASELINE"

        return {
            "risk_score": final_risk_score,
            "risk_category": category,
            "ml_probability": round(ml_probability, 4),
            "is_flagged": is_flagged,
            "detection_method": detection_method,
            "rule_matches": matched_rules,
            "reasons": reasons
        }

ml_service = MLService()
