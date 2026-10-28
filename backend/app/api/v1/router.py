from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    auth, users, transactions, alerts, cases, analytics, ml, audit, health
)

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Fraud Alerts"])
api_router.include_router(cases.router, prefix="/cases", tags=["Investigation Cases"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(ml.router, prefix="/ml", tags=["Machine Learning"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit Logs"])
