from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.analysis import RiskLevel
from app.schemas.analysis import ModalityResultResponse

class ReportBase(BaseModel):
    risk_level: RiskLevel
    global_score: float
    recommendations: Optional[Dict[str, Any]] = None
    full_text: str

class ReportResponse(ReportBase):
    id: UUID
    analysis_id: UUID
    created_at: datetime
    
    # Nested results to return everything the frontend needs
    modality_results: List[ModalityResultResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
