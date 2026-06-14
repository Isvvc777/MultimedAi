import uuid
import io
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.analysis import Report, Analysis
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa

class ReportService:
    def __init__(self):
        # Setup Jinja2 environment for HTML templating
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))

    async def get_full_report(self, analysis_id: uuid.UUID, db: AsyncSession):
        """
        Fetches the Report and all associated ModalityResults for a given analysis_id.
        """
        result = await db.execute(
            select(Report)
            .options(
                selectinload(Report.analysis).selectinload(Analysis.results)
            )
            .where(Report.analysis_id == analysis_id)
        )
        report = result.scalars().first()
        
        if not report:
            return None
            
        # Map to a dictionary matching ReportResponse schema
        return {
            "id": report.id,
            "analysis_id": report.analysis_id,
            "risk_level": report.risk_level,
            "global_score": report.global_score,
            "recommendations": report.recommendations,
            "full_text": report.full_text,
            "created_at": report.created_at,
            "modality_results": report.analysis.results if report.analysis else []
        }

    async def generate_pdf_report(self, analysis_id: uuid.UUID, db: AsyncSession) -> io.BytesIO:
        """
        Generates a PDF byte stream from the report data using an HTML template.
        """
        result = await db.execute(
            select(Report)
            .options(selectinload(Report.analysis).selectinload(Analysis.results))
            .where(Report.analysis_id == analysis_id)
        )
        report = result.scalars().first()
        
        if not report:
            return None

        # Prepare context data
        # We pass raw ORM objects because Jinja2 can easily access their attributes
        context = {
            "report": report,
            "results": report.analysis.results if report.analysis else []
        }

        # Render HTML
        template = self.env.get_template('report.html')
        html_out = template.render(context)
        
        # Convert HTML to PDF
        pdf_file = io.BytesIO()
        pisa_status = pisa.CreatePDF(io.StringIO(html_out), dest=pdf_file)
        
        if pisa_status.err:
            raise Exception(f"PDF Generation Error: {pisa_status.err}")
            
        pdf_file.seek(0)
        return pdf_file

report_service = ReportService()
