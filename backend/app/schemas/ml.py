from datetime import datetime
from typing import Dict, Any, List
from pydantic import BaseModel

class ModelMetricsResponse(BaseModel):
    id: int
    model_name: str
    model_version: str
    algorithm: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    pr_auc: float
    roc_auc: float
    decision_threshold: float
    confusion_matrix: Dict[str, int]
    class_distribution: Dict[str, int]
    feature_importances: List[Dict[str, Any]]
    test_samples_count: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ModelComparisonItem(BaseModel):
    method: str
    precision: float
    recall: float
    f1_score: float
    latency_ms: float
    explainability: str
    advantages: str
    disadvantages: str
