import io
import csv
import json
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from backend.app.models.transaction import Transaction, RiskCategory
from backend.app.schemas.transaction import TransactionCreate
from backend.app.services.ml_service import ml_service
from backend.app.services.alert_service import alert_service
from backend.app.services.audit_service import audit_service
from backend.app.models.user import User
from ml_pipeline.data_generator import generate_synthetic_transactions

class TransactionService:
    @staticmethod
    def process_and_create(
        db: Session,
        txn_in: TransactionCreate,
        actor: Optional[User] = None,
        ip_address: Optional[str] = None
    ) -> Transaction:
        txn_ref = txn_in.transaction_ref or f"TXN-{uuid.uuid4().hex[:8].upper()}"
        timestamp = txn_in.timestamp or datetime.now(timezone.utc)

        # Run Prediction Service (Rules + ML hybrid)
        prediction = ml_service.predict(
            amount=txn_in.amount,
            currency=txn_in.currency,
            timestamp=timestamp,
            transaction_type=txn_in.transaction_type,
            merchant_category=txn_in.merchant_category,
            payment_channel=txn_in.payment_channel,
            country=txn_in.country,
            ip_risk_score=txn_in.ip_risk_score,
            historical_velocity_1h=txn_in.historical_velocity_1h,
            historical_amount_avg=txn_in.historical_amount_avg,
            distance_from_home_km=txn_in.distance_from_home_km,
            failed_attempts_count=txn_in.failed_attempts_count
        )

        txn = Transaction(
            transaction_ref=txn_ref,
            customer_id=txn_in.customer_id,
            amount=txn_in.amount,
            currency=txn_in.currency,
            timestamp=timestamp,
            transaction_type=txn_in.transaction_type,
            merchant_category=txn_in.merchant_category,
            payment_channel=txn_in.payment_channel,
            country=txn_in.country,
            device_id=txn_in.device_id,
            ip_address=txn_in.ip_address,
            ip_risk_score=txn_in.ip_risk_score,
            historical_velocity_1h=txn_in.historical_velocity_1h,
            historical_amount_avg=txn_in.historical_amount_avg,
            distance_from_home_km=txn_in.distance_from_home_km,
            failed_attempts_count=txn_in.failed_attempts_count,
            is_flagged=prediction["is_flagged"],
            risk_score=prediction["risk_score"],
            risk_category=prediction["risk_category"],
            ml_probability=prediction["ml_probability"],
            rule_matches=json.dumps(prediction["rule_matches"]),
            reasons=json.dumps(prediction["reasons"])
        )
        db.add(txn)
        db.commit()
        db.refresh(txn)

        # Automatically spawn Alert if risk exceeds threshold or flagged
        if txn.is_flagged or txn.risk_score >= 60:
            alert_service.create_alert_if_flagged(db, txn)

        return txn

    @staticmethod
    def generate_synthetic(
        db: Session,
        count: int = 50,
        fraud_ratio: float = 0.15,
        actor: Optional[User] = None
    ) -> List[Transaction]:
        df = generate_synthetic_transactions(n_samples=count, fraud_ratio=fraud_ratio)
        created = []
        for _, row in df.iterrows():
            ts = datetime.fromisoformat(row["timestamp"])
            prediction = ml_service.predict(
                amount=float(row["amount"]),
                currency=row["currency"],
                timestamp=ts,
                transaction_type=row["transaction_type"],
                merchant_category=row["merchant_category"],
                payment_channel=row["payment_channel"],
                country=row["country"],
                ip_risk_score=float(row["ip_risk_score"]),
                historical_velocity_1h=int(row["historical_velocity_1h"]),
                historical_amount_avg=float(row["historical_amount_avg"]),
                distance_from_home_km=float(row["distance_from_home_km"]),
                failed_attempts_count=int(row["failed_attempts_count"])
            )
            
            txn = Transaction(
                transaction_ref=row["transaction_ref"],
                customer_id=row["customer_id"],
                amount=float(row["amount"]),
                currency=row["currency"],
                timestamp=ts,
                transaction_type=row["transaction_type"],
                merchant_category=row["merchant_category"],
                payment_channel=row["payment_channel"],
                country=row["country"],
                device_id=row["device_id"],
                ip_address=row["ip_address"],
                ip_risk_score=float(row["ip_risk_score"]),
                historical_velocity_1h=int(row["historical_velocity_1h"]),
                historical_amount_avg=float(row["historical_amount_avg"]),
                distance_from_home_km=float(row["distance_from_home_km"]),
                failed_attempts_count=int(row["failed_attempts_count"]),
                ground_truth_fraud=int(row["ground_truth_fraud"]),
                is_flagged=prediction["is_flagged"],
                risk_score=prediction["risk_score"],
                risk_category=prediction["risk_category"],
                ml_probability=prediction["ml_probability"],
                rule_matches=json.dumps(prediction["rule_matches"]),
                reasons=json.dumps(prediction["reasons"])
            )
            db.add(txn)
            db.flush()
            
            if txn.is_flagged or txn.risk_score >= 60:
                alert_service.create_alert_if_flagged(db, txn)
                
            created.append(txn)

        db.commit()
        if actor:
            audit_service.log(
                db=db,
                event_type="SYNTHETIC_DATA_GENERATED",
                actor=actor,
                entity_type="TRANSACTION",
                description=f"Generated {count} synthetic transactions with {fraud_ratio*100:.1f}% simulated fraud vector."
            )
        return created

    @staticmethod
    def parse_csv_and_import(
        db: Session,
        csv_content: str,
        actor: Optional[User] = None
    ) -> Tuple[int, List[str]]:
        reader = csv.DictReader(io.StringIO(csv_content))
        required_cols = {"customer_id", "amount", "merchant_category", "payment_channel"}
        if not required_cols.issubset(set(reader.fieldnames or [])):
            missing = required_cols - set(reader.fieldnames or [])
            raise ValueError(f"CSV file is missing mandatory columns: {', '.join(missing)}")

        success_count = 0
        errors = []
        row_idx = 1
        
        for row in reader:
            row_idx += 1
            try:
                amount = float(row.get("amount", 0))
                if amount <= 0:
                    errors.append(f"Row {row_idx}: Amount must be positive.")
                    continue

                cust_id = row.get("customer_id", "").strip()
                if not cust_id:
                    errors.append(f"Row {row_idx}: Customer ID cannot be empty.")
                    continue

                ts_str = row.get("timestamp")
                if ts_str:
                    try:
                        ts = datetime.fromisoformat(ts_str)
                    except Exception:
                        ts = datetime.now(timezone.utc)
                else:
                    ts = datetime.now(timezone.utc)

                txn_in = TransactionCreate(
                    customer_id=cust_id,
                    amount=amount,
                    currency=row.get("currency", "INR"),
                    timestamp=ts,
                    transaction_type=row.get("transaction_type", "PAYMENT"),
                    merchant_category=row.get("merchant_category", "RETAIL"),
                    payment_channel=row.get("payment_channel", "MOBILE_APP"),
                    country=row.get("country", "IN"),
                    device_id=row.get("device_id", f"DEV-{uuid.uuid4().hex[:4]}"),
                    ip_address=row.get("ip_address", "192.168.1.1"),
                    ip_risk_score=float(row.get("ip_risk_score", 10.0)),
                    historical_velocity_1h=int(row.get("historical_velocity_1h", 1)),
                    historical_amount_avg=float(row.get("historical_amount_avg", 1000.0)),
                    distance_from_home_km=float(row.get("distance_from_home_km", 5.0)),
                    failed_attempts_count=int(row.get("failed_attempts_count", 0))
                )
                TransactionService.process_and_create(db, txn_in, actor=actor)
                success_count += 1
            except Exception as e:
                errors.append(f"Row {row_idx}: Ingestion failed ({str(e)})")

        if actor:
            audit_service.log(
                db=db,
                event_type="CSV_IMPORT_EXECUTED",
                actor=actor,
                entity_type="TRANSACTION",
                description=f"CSV import processed: {success_count} succeeded, {len(errors)} errors.",
                details={"success_count": success_count, "error_count": len(errors)}
            )
        return success_count, errors

transaction_service = TransactionService()
