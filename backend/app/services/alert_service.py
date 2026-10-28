import json
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.models.alert import Alert, AlertStatus, AlertPriority
from backend.app.models.transaction import Transaction, RiskCategory
from backend.app.models.case import InvestigationCase, CaseStatus, CasePriority, CaseOutcome
from backend.app.models.user import User
from backend.app.services.audit_service import audit_service

class AlertService:
    @staticmethod
    def create_alert_if_flagged(db: Session, transaction: Transaction) -> Optional[Alert]:
        # Only create alert if transaction is flagged or high/critical risk
        if not transaction.is_flagged and transaction.risk_score < 60:
            return None

        # Check if alert already exists for this transaction
        existing = db.query(Alert).filter(Alert.transaction_id == transaction.id).first()
        if existing:
            return existing

        priority = AlertPriority.MEDIUM
        if transaction.risk_category == RiskCategory.CRITICAL:
            priority = AlertPriority.CRITICAL
        elif transaction.risk_category == RiskCategory.HIGH:
            priority = AlertPriority.HIGH
        elif transaction.risk_category == RiskCategory.LOW:
            priority = AlertPriority.LOW

        alert_ref = f"ALT-{uuid.uuid4().hex[:8].upper()}"
        alert = Alert(
            alert_ref=alert_ref,
            transaction_id=transaction.id,
            risk_score=transaction.risk_score,
            risk_category=transaction.risk_category,
            detection_method="HYBRID_ML_RULES",
            reasons=transaction.reasons,
            status=AlertStatus.NEW,
            priority=priority,
            assigned_to_id=None
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)

        # Audit log creation
        audit_service.log(
            db=db,
            event_type="ALERT_CREATED",
            actor=None,
            entity_type="ALERT",
            entity_id=alert.alert_ref,
            description=f"Automated risk alert triggered for transaction {transaction.transaction_ref} (Score: {transaction.risk_score})",
            details={"risk_score": transaction.risk_score, "priority": priority.value}
        )
        return alert

    @staticmethod
    def update_alert(
        db: Session,
        alert: Alert,
        actor: User,
        status: Optional[AlertStatus] = None,
        priority: Optional[AlertPriority] = None,
        assigned_to_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Alert:
        old_status = alert.status
        if status:
            alert.status = status
        if priority:
            alert.priority = priority
        if assigned_to_id is not None:
            alert.assigned_to_id = assigned_to_id
            
        alert.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(alert)

        audit_service.log(
            db=db,
            event_type="ALERT_STATUS_UPDATED",
            actor=actor,
            entity_type="ALERT",
            entity_id=alert.alert_ref,
            description=f"Alert {alert.alert_ref} status changed from {old_status.value} to {alert.status.value}",
            details={"old_status": old_status.value, "new_status": alert.status.value, "notes": notes}
        )
        return alert

alert_service = AlertService()
