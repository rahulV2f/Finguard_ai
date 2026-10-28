import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.api.v1.router import api_router
from backend.app.models import user, transaction, alert, case, audit, model_metrics
from backend.app.services.ml_service import ml_service
from ml_pipeline.train import train_and_evaluate

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables on startup
    Base.metadata.create_all(bind=engine)
    
    # Check if ML model exists, else train an initial balanced Random Forest model
    model_path = os.path.join(settings.MODEL_DIR, "finguard_rf_model.joblib")
    if not os.path.exists(model_path):
        print("FinGuard ML model not found. Training initial model on synthetic banking transactions...")
        try:
            train_and_evaluate(n_samples=2500)
            ml_service.load_artifacts()
        except Exception as e:
            print(f"Initial ML training warning: {e}")
    else:
        ml_service.load_artifacts()
    
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "FinGuard AI: Full-Stack Banking Fraud Detection & Risk Intelligence Simulation Platform. "
        "Strictly uses synthetic anonymized transaction data for educational risk scoring & case investigation."
    ),
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# Restrictive & Flexible CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "detail": str(exc)}
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "docs": f"{settings.API_V1_STR}/docs"
    }
