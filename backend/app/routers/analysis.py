import uuid
import json
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.analysis import Analysis, AnalysisStatus, ModalityResult
from app.schemas.analysis import AnalysisCreateResponse, AnalysisStatusResponse, AnalysisStatusStage
from app.utils.file_handler import file_handler
from app.tasks.analysis_tasks import run_analysis

router = APIRouter(prefix="/analysis", tags=["Analysis"])

@router.post("", response_model=AnalysisCreateResponse)
async def create_analysis(
    image: UploadFile = File(None),
    pdf: UploadFile = File(None),
    symptom_text: str = Form(None),
    sensor_data: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Accepts multipart/form-data for all modalities.
    Uploads files to MinIO, creates DB record, and dispatches Celery task.
    """
    # Validate sensor_data if provided
    sensor_dict = None
    if sensor_data:
        try:
            sensor_dict = json.loads(sensor_data)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid sensor_data JSON format")

    # Ensure at least one modality is provided
    if not any([image, pdf, symptom_text, sensor_dict]):
        raise HTTPException(status_code=400, detail="At least one input modality must be provided")

    analysis_id = uuid.uuid4()
    
    # Upload files asynchronously to MinIO
    image_path = None
    if image:
        image_content = await image.read()
        image_path = await file_handler.upload_file(
            f"analyses/{analysis_id}/image_{image.filename}", 
            image_content, 
            image.content_type
        )
        
    pdf_path = None
    if pdf:
        pdf_content = await pdf.read()
        pdf_path = await file_handler.upload_file(
            f"analyses/{analysis_id}/report_{pdf.filename}", 
            pdf_content, 
            pdf.content_type
        )

    # Save initial analysis state to DB
    analysis = Analysis(
        id=analysis_id,
        status=AnalysisStatus.pending,
        image_path=image_path,
        pdf_path=pdf_path,
        symptom_text=symptom_text,
        sensor_data=sensor_dict
    )
    
    db.add(analysis)
    await db.commit()
    
    # Dispatch the async Celery task
    run_analysis.delay(str(analysis_id))
    
    return AnalysisCreateResponse(
        analysis_id=analysis_id,
        status=AnalysisStatus.pending
    )

@router.get("/{analysis_id}/status", response_model=AnalysisStatusResponse)
async def get_analysis_status(analysis_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Returns the processing status and progress for polling.
    """
    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    analysis = result.scalars().first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    # Estimate progress based on current status and saved modality results
    progress = 0
    if analysis.status == AnalysisStatus.pending:
        progress = 10
    elif analysis.status == AnalysisStatus.processing:
        res = await db.execute(select(ModalityResult).where(ModalityResult.analysis_id == analysis_id))
        results = res.scalars().all()
        # Approx: 20% base processing + 15% per finished modality
        progress = min(20 + len(results) * 15, 95)
    elif analysis.status == AnalysisStatus.done:
        progress = 100
    elif analysis.status == AnalysisStatus.failed:
        progress = 0
        
    # In a full implementation, we can track exact stages. Returning a summary here.
    stages = [
        AnalysisStatusStage(modality="fusion", status=analysis.status.value)
    ]
    
    return AnalysisStatusResponse(
        status=analysis.status,
        progress=progress,
        stages=stages
    )
