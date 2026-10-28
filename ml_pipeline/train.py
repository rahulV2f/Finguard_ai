import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, confusion_matrix, accuracy_score
)
from sklearn.preprocessing import StandardScaler
from ml_pipeline.data_generator import generate_synthetic_transactions

MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "models"))
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "finguard_rf_model.joblib")
SCALER_PATH = os.path.join(MODEL_DIR, "finguard_scaler.joblib")
METRICS_PATH = os.path.join(MODEL_DIR, "metrics.json")

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    features = pd.DataFrame(index=df.index)
    
    # 1. Normalized Amount and ratio to historical baseline
    features["amount"] = df["amount"].astype(float)
    features["historical_amount_avg"] = df["historical_amount_avg"].replace(0, 100).astype(float)
    features["amount_to_hist_ratio"] = features["amount"] / features["historical_amount_avg"]
    
    # 2. Velocity & Geographic deviation
    features["historical_velocity_1h"] = df["historical_velocity_1h"].astype(float)
    features["distance_from_home_km"] = df["distance_from_home_km"].astype(float)
    features["failed_attempts_count"] = df["failed_attempts_count"].astype(float)
    features["ip_risk_score"] = df["ip_risk_score"].astype(float)
    
    # 3. Time-of-day features from timestamp
    timestamps = pd.to_datetime(df["timestamp"])
    features["hour_of_day"] = timestamps.dt.hour
    features["is_night"] = features["hour_of_day"].apply(lambda h: 1.0 if (h >= 1 and h <= 5) else 0.0)
    features["is_weekend"] = timestamps.dt.dayofweek.apply(lambda d: 1.0 if d >= 5 else 0.0)
    
    # 4. Merchant Category risk mapping
    high_risk_merchants = {"GAMBLING": 1.0, "CRYPTO": 1.0, "LUXURY": 0.7, "ELECTRONICS": 0.5, "TRAVEL": 0.4}
    features["merchant_risk_weight"] = df["merchant_category"].map(lambda m: high_risk_merchants.get(m, 0.1))
    
    # 5. Channel risk mapping
    channel_risk = {"UPI": 0.6, "MOBILE_APP": 0.4, "NET_BANKING": 0.5, "ATM": 0.3, "POS_TERMINAL": 0.2}
    features["channel_risk_weight"] = df["payment_channel"].map(lambda c: channel_risk.get(c, 0.2))
    
    # 6. Country mismatch indicator
    features["is_cross_border"] = (df["country"] != "IN").astype(float)
    
    return features

def train_and_evaluate(n_samples: int = 3500, random_seed: int = 42):
    print(f"Generating {n_samples} synthetic banking transactions for model training...")
    df = generate_synthetic_transactions(n_samples=n_samples, fraud_ratio=0.14, random_seed=random_seed)
    
    # Chronological sort to prevent lookahead data leakage
    df = df.sort_values(by="timestamp").reset_index(drop=True)
    
    X = engineer_features(df)
    y = df["ground_truth_fraud"].values
    
    # Chronological Train-Test Split (80% train, 20% test)
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("Training Balanced Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=120,
        max_depth=9,
        min_samples_split=4,
        class_weight="balanced",
        random_state=random_seed,
        n_jobs=-1
    )
    model.fit(X_train_scaled, y_train)
    
    # Inference on held-out test data
    y_probs = model.predict_proba(X_test_scaled)[:, 1]
    
    # Decision threshold
    threshold = 0.48
    y_pred = (y_probs >= threshold).astype(int)
    
    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, y_probs))
    pr_auc = float(average_precision_score(y_test, y_probs))
    
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = int(cm[0, 0]), int(cm[0, 1]), int(cm[1, 0]), int(cm[1, 1])
    
    feature_names = list(X.columns)
    importances = model.feature_importances_
    sorted_importances = sorted(
        [{"feature": name, "importance": round(float(imp), 4)} for name, imp in zip(feature_names, importances)],
        key=lambda x: x["importance"],
        reverse=True
    )
    
    metrics = {
        "model_name": "FinGuard Random Forest Classifier",
        "model_version": "1.0.0",
        "algorithm": "Balanced Random Forest (120 Estimators, max_depth=9)",
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "pr_auc": round(pr_auc, 4),
        "roc_auc": round(roc_auc, 4),
        "decision_threshold": threshold,
        "confusion_matrix": {
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn,
            "true_positives": tp
        },
        "class_distribution": {
            "legitimate_samples": int((y_test == 0).sum()),
            "fraud_samples": int((y_test == 1).sum())
        },
        "feature_importances": sorted_importances,
        "test_samples_count": len(y_test),
        "trained_at": datetime.utcnow().isoformat()
    }
    
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)
        
    print(f"Model saved successfully to {MODEL_PATH}")
    print(f"Evaluation Metrics on Held-out Test Set:")
    print(f"Precision: {prec:.4f} | Recall: {rec:.4f} | F1: {f1:.4f} | PR-AUC: {pr_auc:.4f} | ROC-AUC: {roc_auc:.4f}")
    return metrics

if __name__ == "__main__":
    train_and_evaluate()
