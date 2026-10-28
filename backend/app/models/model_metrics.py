from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, Text
from backend.app.core.database import Base

class ModelEvaluationRun(Base):
    __tablename__ = "model_evaluation_runs"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), default="FinGuard Random Forest Classifier", nullable=False)
    model_version = Column(String(50), default="1.0.0", nullable=False)
    algorithm = Column(String(100), default="Balanced RandomForest / GradientBoosting", nullable=False)
    
    accuracy = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    pr_auc = Column(Float, nullable=False)
    roc_auc = Column(Float, nullable=False)
    decision_threshold = Column(Float, default=0.5, nullable=False)
    
    confusion_matrix_json = Column(Text, default="{}", nullable=False)
    class_distribution_json = Column(Text, default="{}", nullable=False)
    feature_importances_json = Column(Text, default="{}", nullable=False)
    
    test_samples_count = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
