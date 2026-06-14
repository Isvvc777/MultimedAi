import asyncio
import io
import PIL.Image
from sqlalchemy.future import select
from celery import Celery

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.analysis import Analysis, AnalysisStatus, ModalityResult, ModalityType, Report
from app.utils.file_handler import file_handler

from app.services.yolo_service import yolo_service
from app.services.llm_service import llm_service
from app.services.ocr_service import ocr_service
from app.services.sensor_service import sensor_service
from app.services.fusion_service import fusion_service

celery_app = Celery(
    "multimedai_tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

async def _process_analysis_async(analysis_id: str):
    async with AsyncSessionLocal() as db:
        # 1. Load Analysis record
        result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
        analysis = result.scalars().first()
        if not analysis:
            print(f"Analysis {analysis_id} not found.")
            return

        # 2. Set status to processing
        analysis.status = AnalysisStatus.processing
        await db.commit()
        
        try:
            tasks = []
            modality_keys = []
            
            # --- IMAGE MODALITY ---
            if analysis.image_path:
                async def _process_image():
                    img_bytes = await file_handler.download_file(analysis.image_path)
                    img = PIL.Image.open(io.BytesIO(img_bytes)).convert("RGB")
                    detections, risk_score = await yolo_service.analyze_image(img)
                    return {
                        "modality": ModalityType.image,
                        "raw_output": {"detections": detections},
                        "risk_score": risk_score,
                        "confidence": 0.9 if detections else 0.5,
                        "summary": f"Detected {len(detections)} potential risk zones."
                    }
                tasks.append(_process_image())
                modality_keys.append("image")

            # --- PDF / OCR MODALITY ---
            if analysis.pdf_path:
                async def _process_pdf():
                    pdf_bytes = await file_handler.download_file(analysis.pdf_path)
                    data, risk_score, raw_text = await ocr_service.process_pdf(pdf_bytes)
                    return {
                        "modality": ModalityType.pdf,
                        "raw_output": data,
                        "risk_score": risk_score,
                        "confidence": 0.85,
                        "summary": f"Extracted {len(data.get('medications', []))} medications and {len(data.get('diagnoses', []))} diagnoses."
                    }
                tasks.append(_process_pdf())
                modality_keys.append("pdf")

            # --- TEXT SYMPTOMS MODALITY ---
            if analysis.symptom_text:
                async def _process_text():
                    data = await llm_service.analyze_symptoms(analysis.symptom_text)
                    return {
                        "modality": ModalityType.text,
                        "raw_output": data,
                        "risk_score": float(data.get("risk_score", 0.0)),
                        "confidence": 0.8,
                        "summary": f"Extracted {len(data.get('symptoms', []))} reported symptoms."
                    }
                tasks.append(_process_text())
                modality_keys.append("text")

            # --- SENSOR MODALITY ---
            if analysis.sensor_data:
                async def _process_sensors():
                    data, risk_score = await sensor_service.analyze_sensors(analysis.sensor_data)
                    return {
                        "modality": ModalityType.sensor,
                        "raw_output": data,
                        "risk_score": risk_score,
                        "confidence": 0.95,
                        "summary": data.get("summary", "Sensors processed successfully.")
                    }
                tasks.append(_process_sensors())
                modality_keys.append("sensor")

            # 3. RUN ALL MODALITIES IN PARALLEL
            print(f"Executing {len(tasks)} modalities in parallel...")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 4. Save results to DB & collect scores for fusion
            modality_scores = {
                "image": None,
                "text": None,
                "pdf": None,
                "sensor": None
            }
            
            for idx, res in enumerate(results):
                key = modality_keys[idx]
                if isinstance(res, Exception):
                    print(f"Error in modality {key}: {res}")
                    continue
                    
                modality_scores[key] = res["risk_score"]
                
                mod_result = ModalityResult(
                    analysis_id=analysis.id,
                    modality=res["modality"],
                    raw_output=res["raw_output"],
                    risk_score=res["risk_score"],
                    confidence=res["confidence"],
                    summary=res["summary"]
                )
                db.add(mod_result)
            
            await db.commit()

            # 5. Execute Fusion Service
            fusion_data = fusion_service.calculate_global_risk(modality_scores)
            
            # Generate Base Report
            # Note: More complex report generation (PDF layout) might be handled in Step 13/21
            report = Report(
                analysis_id=analysis.id,
                risk_level=fusion_data["risk_level"],
                global_score=fusion_data["global_score"],
                recommendations={"note": "Automated AI fusion complete. Review individual modalities for details."},
                full_text=f"Global Risk Score: {fusion_data['global_score']}\nRisk Level: {fusion_data['risk_level'].value.upper()}"
            )
            db.add(report)

            # 6. Set status = done
            analysis.status = AnalysisStatus.done
            await db.commit()
            print(f"Analysis {analysis_id} completed successfully.")

        except Exception as e:
            print(f"Analysis {analysis_id} failed catastrophically: {e}")
            analysis.status = AnalysisStatus.failed
            await db.commit()

@celery_app.task
def run_analysis(analysis_id: str):
    """
    Synchronous Celery task entrypoint that wraps the async processor.
    """
    asyncio.run(_process_analysis_async(analysis_id))
