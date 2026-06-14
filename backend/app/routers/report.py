import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.report import ReportResponse
from app.services.report_service import report_service

router = APIRouter(prefix="/report", tags=["Report"])

@router.get("/{analysis_id}", response_model=ReportResponse)
async def get_report(analysis_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Fetches the final risk report and all detailed modality results.
    """
    report_data = await report_service.get_full_report(analysis_id, db)
    
    if not report_data:
        raise HTTPException(status_code=404, detail="Report not found or not yet generated.")
        
    return report_data

@router.get("/{analysis_id}/pdf")
async def get_report_pdf(analysis_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Generates and returns a PDF version of the report.
    """
    pdf_stream = await report_service.generate_pdf_report(analysis_id, db)
    
    if not pdf_stream:
        raise HTTPException(status_code=404, detail="Report not found.")
        
    return StreamingResponse(
        pdf_stream,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=MultiMedAI_Report_{analysis_id}.pdf"
        }
    )
