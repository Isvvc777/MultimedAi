from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from typing import Optional, List, Dict, Any
from app.models.analysis import AnalysisStatus, ModalityType

class ModalityResultBase(BaseModel):
    modality: ModalityType
    raw_output: Optional[Dict[str, Any]] = None
    risk_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    summary: Optional[str] = None

class ModalityResultResponse(ModalityResultBase):
    id: UUID
    analysis_id: UUID
    
    model_config = ConfigDict(from_attributes=True)

class AnalysisCreateResponse(BaseModel):
    analysis_id: UUID
    status: AnalysisStatus

class AnalysisStatusStage(BaseModel):
    modality: ModalityType
    status: str

class AnalysisStatusResponse(BaseModel):
    status: AnalysisStatus
    progress: int = Field(ge=0, le=100)
    stages: List[AnalysisStatusStage]

class ChatMessageRequest(BaseModel):
    analysis_id: UUID
    message: str
    history: List[Dict[str, str]] = []  # e.g., [{"role": "user", "content": "hello"}]
