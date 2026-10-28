from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status, Response, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from backend.app.api.deps import get_db, get_current_user, get_current_analyst
from backend.app.models.transaction import Transaction, RiskCategory
from backend.app.models.user import User
from backend.app.schemas.transaction import (
    TransactionCreate, TransactionResponse, TransactionListResponse,
    PredictionResponse, SyntheticGenerateRequest
)
from backend.app.services.transaction_service import transaction_service
from backend.app.services.ml_service import ml_service

router = APIRouter()

@router.get("/", response_model=TransactionListResponse)
def get_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    risk_category: Optional[RiskCategory] = None,
    payment_channel: Optional[str] = None,
    merchant_category: Optional[str] = None,
    is_flagged: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Transaction)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Transaction.transaction_ref.ilike(search_filter),
                Transaction.customer_id.ilike(search_filter),
                Transaction.merchant_category.ilike(search_filter),
                Transaction.device_id.ilike(search_filter)
            )
        )
    if risk_category:
        query = query.filter(Transaction.risk_category == risk_category)
    if payment_channel:
        query = query.filter(Transaction.payment_channel == payment_channel)
    if merchant_category:
        query = query.filter(Transaction.merchant_category == merchant_category)
    if is_flagged is not None:
        query = query.filter(Transaction.is_flagged == is_flagged)
        
    total = query.count()
    items = query.order_by(desc(Transaction.timestamp)).offset((page - 1) * page_size).limit(page_size).all()
    pages = (total + page_size - 1) // page_size if total > 0 else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }

@router.get("/{txn_id}", response_model=TransactionResponse)
def get_transaction_detail(
    txn_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    txn = db.query(Transaction).filter(Transaction.id == txn_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    txn_in: TransactionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_analyst)
):
    client_ip = request.client.host if request.client else None
    return transaction_service.process_and_create(db, txn_in, actor=current_user, ip_address=client_ip)

@router.post("/predict", response_model=PredictionResponse)
def predict_risk(
    txn_in: TransactionCreate,
    current_user: User = Depends(get_current_user)
):
    from datetime import datetime, timezone
    ts = txn_in.timestamp or datetime.now(timezone.utc)
    return ml_service.predict(
        amount=txn_in.amount,
        currency=txn_in.currency,
        timestamp=ts,
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

@router.post("/generate-synthetic", response_model=List[TransactionResponse])
def generate_synthetic_data(
    req: SyntheticGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_analyst)
):
    created = transaction_service.generate_synthetic(
        db, count=req.count, fraud_ratio=req.fraud_ratio, actor=current_user
    )
    return created

@router.post("/upload-csv")
async def upload_transactions_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_analyst)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported")
    
    content_bytes = await file.read()
    csv_text = content_bytes.decode("utf-8", errors="replace")
    
    try:
        success_count, errors = transaction_service.parse_csv_and_import(db, csv_text, actor=current_user)
        return {
            "message": f"Successfully ingested {success_count} transactions",
            "imported_count": success_count,
            "errors": errors[:20]  # First 20 errors
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sample-csv/download")
def download_sample_csv():
    csv_data = (
        "customer_id,amount,currency,timestamp,transaction_type,merchant_category,payment_channel,country,device_id,ip_address,ip_risk_score,historical_velocity_1h,historical_amount_avg,distance_from_home_km,failed_attempts_count\n"
        "CUST-0012,450.00,INR,2026-10-25T14:30:00Z,PAYMENT,GROCERY,UPI,IN,DEV-1001,192.168.1.5,12.0,1,1200.0,3.5,0\n"
        "CUST-0044,48900.00,INR,2026-10-25T02:15:00Z,TRANSFER,CRYPTO,NET_BANKING,IN,DEV-UNKNOWN,192.168.1.99,92.5,7,1500.0,450.0,4\n"
        "CUST-0089,1850.00,INR,2026-10-25T11:05:00Z,POS,DINING,POS_TERMINAL,IN,DEV-2041,192.168.1.20,8.0,1,2000.0,2.1,0\n"
        "CUST-0105,75000.00,INR,2026-10-25T19:40:00Z,PAYMENT,LUXURY,MOBILE_APP,AE,DEV-9988,192.168.1.75,85.0,5,2500.0,2400.0,2\n"
    )
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=finguard_sample_transactions.csv"}
    )
