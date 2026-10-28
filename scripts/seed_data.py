import os
import sys
from datetime import datetime, timezone

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.database import engine, SessionLocal, Base
from backend.app.models.user import User, UserRole
from backend.app.models.transaction import Transaction
from backend.app.models.alert import Alert, AlertStatus, AlertPriority
from backend.app.models.case import InvestigationCase, CaseStatus, CasePriority, CaseOutcome, CaseNote
from backend.app.models.audit import AuditLog
from backend.app.core.security import get_password_hash
from backend.app.core.config import settings
from backend.app.services.transaction_service import transaction_service
from backend.app.services.case_service import case_service
from ml_pipeline.train import train_and_evaluate, MODEL_PATH

def seed_database():
    print("=" * 60)
    print("FinGuard AI: Initializing Database & Seeding Simulation Data")
    print("=" * 60)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed or update Demo Users
        admin_user = db.query(User).filter(User.email == settings.DEMO_ADMIN_EMAIL).first()
        if not admin_user:
            admin_user = User(
                email=settings.DEMO_ADMIN_EMAIL,
                full_name="Chief Risk Officer (Admin)",
                hashed_password=get_password_hash(settings.DEMO_ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            print(f"[+] Created Admin: {settings.DEMO_ADMIN_EMAIL} / {settings.DEMO_ADMIN_PASSWORD}")
        
        analyst_user = db.query(User).filter(User.email == settings.DEMO_ANALYST_EMAIL).first()
        if not analyst_user:
            analyst_user = User(
                email=settings.DEMO_ANALYST_EMAIL,
                full_name="Senior Fraud Investigator",
                hashed_password=get_password_hash(settings.DEMO_ANALYST_PASSWORD),
                role=UserRole.ANALYST,
                is_active=True
            )
            db.add(analyst_user)
            print(f"[+] Created Analyst: {settings.DEMO_ANALYST_EMAIL} / {settings.DEMO_ANALYST_PASSWORD}")
        
        db.commit()
        db.refresh(admin_user)
        db.refresh(analyst_user)

        # 2. Check and train ML model
        if not os.path.exists(MODEL_PATH):
            print("\n[+] Training FinGuard Random Forest Model on Synthetic Banking Data...")
            train_and_evaluate(n_samples=2500)
        else:
            print("[+] Found existing trained ML model artifact.")

        # 3. Seed Transactions if table has fewer than 20 rows
        txn_count = db.query(Transaction).count()
        if txn_count < 20:
            print("\n[+] Generating initial pool of 120 synthetic transactions...")
            txns = transaction_service.generate_synthetic(
                db=db,
                count=120,
                fraud_ratio=0.18,
                actor=admin_user
            )
            print(f"[+] Ingested {len(txns)} transactions into database.")

        # 4. Seed sample cases for pending alerts
        unassigned_alerts = db.query(Alert).filter(Alert.investigation_case == None).limit(5).all()
        for idx, alert in enumerate(unassigned_alerts):
            case = case_service.create_case(
                db=db,
                alert_id=alert.id,
                title=f"Suspicious {alert.transaction.merchant_category} activity on {alert.transaction.customer_id}",
                actor=analyst_user,
                priority=CasePriority.HIGH,
                assigned_to_id=analyst_user.id
            )
            case_service.add_note(
                db=db,
                case=case,
                actor=analyst_user,
                note_text="Initial automated triage completed. Contacted synthetic cardholder verification channel."
            )
            if idx == 0:
                case_service.update_case(
                    db=db,
                    case=case,
                    actor=analyst_user,
                    status=CaseStatus.INVESTIGATING,
                    outcome=CaseOutcome.PENDING
                )
            elif idx == 1:
                case_service.update_case(
                    db=db,
                    case=case,
                    actor=analyst_user,
                    status=CaseStatus.CLOSED_FRAUD,
                    outcome=CaseOutcome.FRAUD_CONFIRMED,
                    resolution_notes="Customer confirmed unauthorized foreign card skimming."
                )

        print("\n" + "=" * 60)
        print("FinGuard AI database successfully seeded and operational!")
        print(f"Admin Credentials:   {settings.DEMO_ADMIN_EMAIL}   / {settings.DEMO_ADMIN_PASSWORD}")
        print(f"Analyst Credentials: {settings.DEMO_ANALYST_EMAIL} / {settings.DEMO_ANALYST_PASSWORD}")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"[!] Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
