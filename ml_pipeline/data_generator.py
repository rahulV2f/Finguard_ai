import random
import uuid
from datetime import datetime, timedelta, timezone
import pandas as pd
import numpy as np

CHANNELS = ["MOBILE_APP", "NET_BANKING", "ATM", "POS_TERMINAL", "UPI"]
MERCHANT_CATS = ["GROCERY", "ELECTRONICS", "GAMBLING", "LUXURY", "TRAVEL", "CRYPTO", "UTILITIES", "DINING"]
TXN_TYPES = ["PAYMENT", "TRANSFER", "WITHDRAWAL", "POS", "ONLINE_PURCHASE"]
COUNTRIES = ["IN", "IN", "IN", "IN", "US", "GB", "AE", "SG"]

def generate_synthetic_transactions(n_samples: int = 2000, fraud_ratio: float = 0.12, random_seed: int = 42) -> pd.DataFrame:
    random.seed(random_seed)
    np.random.seed(random_seed)
    
    rows = []
    base_time = datetime.now(timezone.utc) - timedelta(days=30)
    
    # 150 synthetic customer profiles with typical baseline habits
    customers = {}
    for i in range(1, 151):
        c_id = f"CUST-{i:04d}"
        customers[c_id] = {
            "avg_amount": random.uniform(300, 4500),
            "home_country": "IN",
            "primary_device": f"DEV-{random.randint(1000, 9999)}"
        }
    
    c_ids = list(customers.keys())
    
    for i in range(n_samples):
        txn_id = f"TXN-{100000 + i}"
        cust_id = random.choice(c_ids)
        cust_profile = customers[cust_id]
        
        # Determine if this sample is fraudulent based on probability
        is_fraud = 1 if (random.random() < fraud_ratio) else 0
        
        # Generate timestamp spread over the last 30 days
        day_offset = random.uniform(0, 30)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        txn_time = base_time + timedelta(days=day_offset, hours=hour, minutes=minute, seconds=second)
        
        if is_fraud:
            # Fraud patterns: pick one or a combination of fraud vectors
            fraud_type = random.choice([
                "VELOCITY_SPIKE",
                "AMOUNT_ANOMALY",
                "GEO_IMPOSSIBILITY",
                "MIDNIGHT_HIGH_RISK",
                "DEVICE_HOPPING"
            ])
            
            if fraud_type == "VELOCITY_SPIKE":
                amount = cust_profile["avg_amount"] * random.uniform(2.5, 6.0)
                velocity = random.randint(5, 12)
                distance = random.uniform(20, 150)
                failed_attempts = random.randint(1, 3)
                ip_risk = random.uniform(65, 95)
                merchant = random.choice(["ELECTRONICS", "LUXURY", "CRYPTO"])
                channel = random.choice(["UPI", "MOBILE_APP"])
                device = f"DEV-{random.randint(9000, 9999)}"
                country = cust_profile["home_country"]
                
            elif fraud_type == "AMOUNT_ANOMALY":
                amount = cust_profile["avg_amount"] * random.uniform(12.0, 45.0)
                velocity = random.randint(1, 4)
                distance = random.uniform(5, 60)
                failed_attempts = random.randint(0, 2)
                ip_risk = random.uniform(50, 85)
                merchant = random.choice(["LUXURY", "CRYPTO", "GAMBLING"])
                channel = random.choice(["NET_BANKING", "TRANSFER"])
                device = cust_profile["primary_device"]
                country = cust_profile["home_country"]
                
            elif fraud_type == "GEO_IMPOSSIBILITY":
                amount = cust_profile["avg_amount"] * random.uniform(1.8, 8.0)
                velocity = random.randint(2, 5)
                distance = random.uniform(1200, 6500)
                failed_attempts = random.randint(1, 4)
                ip_risk = random.uniform(70, 99)
                merchant = random.choice(["TRAVEL", "LUXURY", "ELECTRONICS"])
                channel = random.choice(["NET_BANKING", "POS_TERMINAL"])
                device = f"DEV-ANON-{random.randint(100, 999)}"
                country = random.choice(["US", "GB", "AE", "SG", "RU"])
                
            elif fraud_type == "MIDNIGHT_HIGH_RISK":
                amount = cust_profile["avg_amount"] * random.uniform(4.0, 15.0)
                velocity = random.randint(3, 7)
                distance = random.uniform(40, 300)
                failed_attempts = random.randint(2, 5)
                ip_risk = random.uniform(75, 98)
                merchant = random.choice(["GAMBLING", "CRYPTO"])
                channel = "MOBILE_APP"
                device = f"DEV-{random.randint(8000, 8999)}"
                country = cust_profile["home_country"]
                # Force late night hours: 01:00 to 04:00
                txn_time = txn_time.replace(hour=random.choice([1, 2, 3, 4]))
                
            else: # DEVICE_HOPPING
                amount = cust_profile["avg_amount"] * random.uniform(3.0, 9.0)
                velocity = random.randint(4, 9)
                distance = random.uniform(100, 500)
                failed_attempts = random.randint(3, 6)
                ip_risk = random.uniform(80, 95)
                merchant = random.choice(["ELECTRONICS", "ONLINE_PURCHASE", "CRYPTO"])
                channel = random.choice(["MOBILE_APP", "UPI"])
                device = f"UNKNOWN-EMULATOR-{random.randint(10, 99)}"
                country = cust_profile["home_country"]
        else:
            # Normal legitimate banking activity
            amount = max(50.0, np.random.normal(cust_profile["avg_amount"], cust_profile["avg_amount"] * 0.35))
            velocity = random.choices([1, 2, 3], weights=[0.8, 0.16, 0.04])[0]
            distance = max(0.5, np.random.exponential(scale=6.0))
            failed_attempts = random.choices([0, 1], weights=[0.95, 0.05])[0]
            ip_risk = max(0.0, min(100.0, np.random.normal(12.0, 8.0)))
            merchant = random.choices(
                ["GROCERY", "DINING", "UTILITIES", "RETAIL", "ELECTRONICS", "TRAVEL"],
                weights=[0.35, 0.25, 0.20, 0.10, 0.06, 0.04]
            )[0]
            channel = random.choice(CHANNELS)
            device = cust_profile["primary_device"]
            country = cust_profile["home_country"]
            
        rows.append({
            "transaction_ref": txn_id,
            "customer_id": cust_id,
            "amount": round(float(amount), 2),
            "currency": "INR",
            "timestamp": txn_time.isoformat(),
            "transaction_type": random.choice(TXN_TYPES),
            "merchant_category": merchant,
            "payment_channel": channel,
            "country": country,
            "device_id": device,
            "ip_address": f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
            "ip_risk_score": round(float(ip_risk), 1),
            "historical_velocity_1h": int(velocity),
            "historical_amount_avg": round(float(cust_profile["avg_amount"]), 2),
            "distance_from_home_km": round(float(distance), 1),
            "failed_attempts_count": int(failed_attempts),
            "ground_truth_fraud": int(is_fraud)
        })
        
    df = pd.DataFrame(rows)
    return df

if __name__ == "__main__":
    df = generate_synthetic_transactions(1000)
    print(f"Generated {len(df)} transactions. Fraud count: {df['ground_truth_fraud'].sum()} ({df['ground_truth_fraud'].mean()*100:.2f}%)")
