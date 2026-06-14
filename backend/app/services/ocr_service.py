import asyncio
import numpy as np
from typing import Dict, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Reuse the LLM engine configured in llm_service
from app.services.llm_service import llm_service

class OCRExtractedData(BaseModel):
    medications: list[str] = Field(description="List of extracted medications")
    lab_values: list[str] = Field(description="List of extracted laboratory values with units")
    diagnoses: list[str] = Field(description="List of extracted diagnoses or medical conditions")
    dates: list[str] = Field(description="List of extracted dates")
    risk_score: float = Field(description="Overall risk score between 0.0 and 1.0 based on the extracted medical data")

class OCRService:
    def __init__(self):
        try:
            from paddleocr import PaddleOCR
            from pdf2image import convert_from_bytes
            # lang='fr' is usually good enough for French + English (PaddleOCR multilingual)
            self.ocr = PaddleOCR(use_angle_cls=True, lang='fr', show_log=False)
            self.convert_func = convert_from_bytes
        except Exception as e:
            print(f"Failed to initialize PaddleOCR: {e}")
            self.ocr = None
            self.convert_func = None

        self.parser = JsonOutputParser(pydantic_object=OCRExtractedData)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a medical data extraction assistant. Analyze the raw OCR text from a medical report and extract medications, lab_values, diagnoses, dates, and compute a risk_score (0.0 to 1.0).\n{format_instructions}"),
            ("human", "Raw OCR Text:\n{text}")
        ])
        
        # Link the prompt to the existing LLM and the JSON parser
        self.chain = self.prompt | llm_service.llm | self.parser

    async def process_pdf(self, pdf_bytes: bytes) -> Tuple[Dict[str, Any], float, str]:
        """
        Converts PDF to images, runs PaddleOCR, and extracts medical entities via LLM.
        Returns: (extracted_json, risk_score, raw_text)
        """
        def _run_ocr():
            if not self.ocr:
                return "OCR initialization failed."
            
            # Note: requires 'poppler-utils' installed on the OS
            images = self.convert_func(pdf_bytes)
            full_text = []
            
            for img in images:
                # Convert PIL Image to Numpy array (RGB)
                img_np = np.array(img)
                # Run OCR
                result = self.ocr.ocr(img_np, cls=True)
                
                # result is a list of lines: [box, (text, confidence)]
                if result and result[0]:
                    for line in result[0]:
                        text = line[1][0]
                        full_text.append(text)
                        
            return "\n".join(full_text)

        # 1. Run OCR (CPU heavy, offload to thread)
        raw_text = await asyncio.to_thread(_run_ocr)
        
        if not raw_text or raw_text == "OCR initialization failed.":
            return {"error": "No text extracted"}, 0.0, raw_text

        # 2. Pass extracted text to LLM
        try:
            # We truncate to 4000 chars to avoid LLM context limits if the PDF is huge
            extracted_data = await self.chain.ainvoke({
                "text": raw_text[:4000], 
                "format_instructions": self.parser.get_format_instructions()
            })
            risk_score = float(extracted_data.get("risk_score", 0.0))
            return extracted_data, risk_score, raw_text
            
        except Exception as e:
            print(f"LLM extraction error during OCR: {e}")
            fallback_data = {
                "medications": [],
                "lab_values": [],
                "diagnoses": ["Error processing text"],
                "dates": [],
                "risk_score": 0.5
            }
            return fallback_data, 0.5, raw_text

ocr_service = OCRService()
