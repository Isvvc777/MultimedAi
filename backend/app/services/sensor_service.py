import asyncio
from typing import Dict, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Reuse the LLM engine
from app.services.llm_service import llm_service

class SensorNarrative(BaseModel):
    summary: str = Field(description="A short medical summary explaining the sensor data and any reasons for concern.")
    recommendation: str = Field(description="Actionable advice based on the sensor vitals.")

class SensorService:
    def __init__(self):
        self.parser = JsonOutputParser(pydantic_object=SensorNarrative)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a medical assistant interpreting patient vital signs. Given the following sensor data and calculated risk score, provide a short medical summary and a recommendation.\n{format_instructions}"),
            ("human", "Sensor Data: {sensor_data}\nCalculated Risk Score (0.0-1.0): {risk_score}")
        ])
        
        self.chain = self.prompt | llm_service.llm | self.parser

    async def analyze_sensors(self, sensor_data: Dict[str, Any]) -> Tuple[Dict[str, Any], float]:
        """
        Calculates rule-based risk score and generates an LLM narrative.
        Returns: (narrative_dict, risk_score)
        """
        if not sensor_data:
            return {"summary": "No sensor data provided.", "recommendation": "None"}, 0.0

        risk_score = 0.0
        
        # SpO2 Rules
        spo2 = float(sensor_data.get("spo2", 100)) # default healthy
        if spo2 < 94:
            risk_score += 0.4
        elif 94 <= spo2 <= 96:
            risk_score += 0.2
            
        # Temperature Rules
        temp = float(sensor_data.get("temperature", 37.0))
        if temp > 39.0:
            risk_score += 0.4
        elif 38.0 <= temp <= 39.0:
            risk_score += 0.2
            
        # BPM (Heart Rate) Rules
        bpm = float(sensor_data.get("bpm", 80))
        if bpm > 0 and (bpm < 50 or bpm > 120):
            risk_score += 0.35
            
        # Sleep Rules
        sleep = float(sensor_data.get("sleep_hours", 8))
        if sleep > 0 and sleep < 4:
            risk_score += 0.1
            
        # Final sensor score capped at 1.0
        risk_score = min(risk_score, 1.0)
        
        # Generate LLM Narrative asynchronously
        try:
            narrative = await self.chain.ainvoke({
                "sensor_data": str(sensor_data),
                "risk_score": risk_score,
                "format_instructions": self.parser.get_format_instructions()
            })
        except Exception as e:
            print(f"LLM narrative error for sensors: {e}")
            narrative = {
                "summary": f"Raw data processed. Rules computed a risk score of {risk_score}.",
                "recommendation": "If symptoms persist, consult a healthcare professional."
            }
            
        return narrative, risk_score

sensor_service = SensorService()
