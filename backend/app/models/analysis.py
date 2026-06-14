import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, Enum, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base

class AnalysisStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    failed = "failed"

class ModalityType(str, enum.Enum):
    image = "image"
    text = "text"
    pdf = "pdf"
    sensor = "sensor"
    fusion = "fusion"

class RiskLevel(str, enum.Enum):
    normal = "normal"
    surveiller = "surveiller"
    urgent = "urgent"

class ChatRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.pending)
    
    image_path = Column(String, nullable=True)
    pdf_path = Column(String, nullable=True)
    symptom_text = Column(Text, nullable=True)
    sensor_data = Column(JSONB, nullable=True)

    # Relationships
    results = relationship("ModalityResult", back_populates="analysis", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    messages = relationship("ChatMessage", back_populates="analysis", cascade="all, delete-orphan")

class ModalityResult(Base):
    __tablename__ = "modality_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"), nullable=False)
    modality = Column(Enum(ModalityType), nullable=False)
    
    raw_output = Column(JSONB, nullable=True)
    risk_score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    summary = Column(Text, nullable=True)

    # Relationships
    analysis = relationship("Analysis", back_populates="results")

class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"), unique=True, nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    global_score = Column(Float, nullable=False)
    
    recommendations = Column(JSONB, nullable=True)
    full_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    analysis = relationship("Analysis", back_populates="report")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"), nullable=False)
    role = Column(Enum(ChatRole), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    analysis = relationship("Analysis", back_populates="messages")
