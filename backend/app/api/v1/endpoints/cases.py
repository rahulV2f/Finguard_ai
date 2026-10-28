from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.api.deps import get_db, get_current_user, get_current_analyst
from backend.app.models.case import InvestigationCase, CaseStatus, CasePriority, CaseOutcome, CaseNote
from backend.app.models.user import User
from backend.app.schemas.case import (
    CaseResponse, CaseListResponse, CaseCreate, CaseUpdate, CaseNoteCreate, CaseNoteResponse
)
from backend.app.services.case_service import case_service

router = APIRouter()

@router.get("/", response_model=CaseListResponse)
def get_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[CaseStatus] = None,
    priority: Optional[CasePriority] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(InvestigationCase)
    if status:
        query = query.filter(InvestigationCase.status == status)
    if priority:
        query = query.filter(InvestigationCase.priority == priority)
        
    total = query.count()
    items = query.order_by(desc(InvestigationCase.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    pages = (total + page_size - 1) // page_size if total > 0 else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }

@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(
    case_in: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_analyst)
):
    try:
        return case_service.create_case(
            db=db,
            alert_id=case_in.alert_id,
            title=case_in.title,
            actor=current_user,
            priority=case_in.priority,
            assigned_to_id=case_in.assigned_to_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{case_id}", response_model=CaseResponse)
def get_case_detail(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    case = db.query(InvestigationCase).filter(InvestigationCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Investigation case not found")
    return case

@router.patch("/{case_id}", response_model=CaseResponse)
def update_case(
    case_id: int,
    case_in: CaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_analyst)
):
    case = db.query(InvestigationCase).filter(InvestigationCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Investigation case not found")
        
    return case_service.update_case(
        db=db,
        case=case,
        actor=current_user,
        status=case_in.status,
        priority=case_in.priority,
        assigned_to_id=case_in.assigned_to_id,
        outcome=case_in.outcome,
        resolution_notes=case_in.resolution_notes
    )

@router.post("/{case_id}/notes", response_model=CaseNoteResponse, status_code=status.HTTP_201_CREATED)
def add_case_note(
    case_id: int,
    note_in: CaseNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_analyst)
):
    case = db.query(InvestigationCase).filter(InvestigationCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Investigation case not found")
        
    return case_service.add_note(
        db=db,
        case=case,
        actor=current_user,
        note_text=note_in.note
    )
