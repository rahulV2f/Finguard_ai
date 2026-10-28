from fastapi import APIRouter
from backend.app.core.config import settings

router = APIRouter()

@router.get("/")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": "simulation_banking_dev"
    }
