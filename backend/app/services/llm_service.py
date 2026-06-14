from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.config import settings

class SymptomInfo(BaseModel):
    name: str = Field(description="Name of the symptom")
    duration: str = Field(description="Duration of the symptom if mentioned, else 'unknown'")
    severity: int = Field(description="Severity from 1 to 10. Default to 5 if not specified.")

class ExtractedSymptoms(BaseModel):
    symptoms: List[SymptomInfo] = Field(description="List of extracted symptoms")
    risk_keywords: List[str] = Field(description="Keywords indicating risk or severity")
    urgency_signals: List[str] = Field(description="Signs that require immediate medical attention")
    risk_score: float = Field(description="Overall risk score between 0.0 and 1.0 based on symptoms")

class LLMService:
    def __init__(self):
        # Fallback mechanism: use OpenAI if key is provided, else use local Ollama
        if settings.openai_api_key:
            print("LLM Service: Initializing with OpenAI (OPENAI_API_KEY detected)")
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                api_key=settings.openai_api_key,
                temperature=0.1
            )
        else:
            print(f"LLM Service: Initializing with local Ollama at {settings.ollama_base_url}")
            self.llm = ChatOllama(
                base_url=settings.ollama_base_url,
                model="llama3.1:8b",
                temperature=0.1,
                format="json"  # Ensure Ollama knows to output JSON
            )
            
        self.parser = JsonOutputParser(pydantic_object=ExtractedSymptoms)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a specialized medical NLP extractor. Extract the symptoms, risk keywords, urgency signals, and calculate a risk_score (0.0 to 1.0) from the patient's text.\n{format_instructions}"),
            ("human", "{text}")
        ])
        
        self.chain = self.prompt | self.llm | self.parser

    async def analyze_symptoms(self, text: str) -> Dict[str, Any]:
        """
        Takes raw symptom text and extracts structured JSON using the LLM.
        """
        # If the user sends an empty string or no text
        if not text or not text.strip():
            return {
                "symptoms": [],
                "risk_keywords": [],
                "urgency_signals": [],
                "risk_score": 0.0
            }

        try:
            result = await self.chain.ainvoke({
                "text": text,
                "format_instructions": self.parser.get_format_instructions()
            })
            return result
        except Exception as e:
            print(f"LLM extraction error: {e}")
            # Fallback safe response if LLM fails
            return {
                "symptoms": [{"name": "Error extracting", "duration": "unknown", "severity": 5}],
                "risk_keywords": [],
                "urgency_signals": [],
                "risk_score": 0.5
            }

llm_service = LLMService()
