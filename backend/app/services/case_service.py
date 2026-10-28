import uuid
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.models.case import InvestigationCase, CaseStatus, CasePriority, CaseOutcome, CaseNote
from backend.app.models.alert import Alert, AlertStatus
from backend.app.models.user import User
from backend.app.services.audit_service import audit_service

class CaseService:
    @staticmethod
    def create_case(
        db: Session,
        alert_id: int,
        title: str,
        actor: User,
        priority: CasePriority = CasePriority.HIGH,
        assigned_to_id: Optional[int] = None
    ) -> InvestigationCase:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise ValueError("Associated Alert not found")

        existing = db.query(InvestigationCase).filter(InvestigationCase.alert_id == alert_id).first()
        if existing:
            return existing

        case_ref = f"CASE-{uuid.uuid4().hex[:8].upper()}"
        case = InvestigationCase(
            case_ref=case_ref,
            alert_id=alert_id,
            title=title,
            status=CaseStatus.OPEN,
            priority=priority,
            assigned_to_id=assigned_to_id or actor.id,
            outcome=CaseOutcome.PENDING
        )
        db.add(case)
        
        # Also mark alert as UNDER_REVIEW
        alert.status = AlertStatus.UNDER_REVIEW
        alert.assigned_to_id = case.assigned_to_id
        db.commit()
        db.refresh(case)

        audit_service.log(
            db=db,
            event_type="CASE_OPENED",
            actor=actor,
            entity_type="CASE",
            entity_id=case.case_ref,
            description=f"Investigation case {case.case_ref} opened for Alert {alert.alert_ref}",
            details={"title": title, "alert_ref": alert.alert_ref}
        )
        return case

    @staticmethod
    def add_note(
        db: Session,
        case: InvestigationCase,
        actor: User,
        note_text: str
    ) -> CaseNote:
        note = CaseNote(
            case_id=case.id,
            user_id=actor.id,
            author_name=actor.full_name,
            note=note_text
        )
        db.add(note)
        case.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(note)

        audit_service.log(
            db=db,
            event_type="CASE_NOTE_ADDED",
            actor=actor,
            entity_type="CASE",
            entity_id=case.case_ref,
            description=f"Analyst note recorded on Case {case.case_ref}"
        )
        return note

    @staticmethod
    def update_case(
        db: Session,
        case: InvestigationCase,
        actor: User,
        status: Optional[CaseStatus] = None,
        priority: Optional[CasePriority] = None,
        assigned_to_id: Optional[int] = None,
        outcome: Optional[CaseOutcome] = None,
        resolution_notes: Optional[str] = None
    ) -> InvestigationCase:
        if status:
            case.status = status
            if status in [CaseStatus.CLOSED_FRAUD, CaseStatus.CLOSED_LEGITIMATE]:
                case.closed_at = datetime.now(timezone.utc)
                if case.alert:
                    if status == CaseStatus.CLOSED_FRAUD:
                        case.alert.status = AlertStatus.CONFIRMED_FRAUD
                        case.outcome = CaseOutcome.FRAUD_CONFIRMED
                    else:
                        case.alert.status = AlertStatus.FALSE_POSITIVE
                        case.outcome = CaseOutcome.FALSE_POSITIVE
        if priority:
            case.priority = priority
        if assigned_to_id is not None:
            case.assigned_to_id = assigned_to_id
        if outcome:
            case.outcome = outcome
        if resolution_notes:
            case.resolution_notes = resolution_notes

        case.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(case)

        audit_service.log(
            db=db,
            event_type="CASE_UPDATED",
            actor=actor,
            entity_type="CASE",
            entity_id=case.case_ref,
            description=f"Investigation Case {case.case_ref} updated. Status: {case.status.value}, Outcome: {case.outcome.value}"
        )
        return case

case_service = CaseService()
