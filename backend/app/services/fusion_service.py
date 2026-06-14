from typing import Dict, Optional
from app.config import settings
from app.models.analysis import RiskLevel

class FusionService:
    def __init__(self):
        # Base weights from application settings
        self.base_weights = {
            "image": settings.weight_image,
            "text": settings.weight_text,
            "pdf": settings.weight_pdf,
            "sensor": settings.weight_sensor
        }

    def calculate_global_risk(self, modality_scores: Dict[str, Optional[float]]) -> dict:
        """
        Calculates the global risk score using weighted fusion.
        If a modality is absent (score is None), its weight is skipped.
        Dividing by `sum_of_active_weights` automatically redistributes the missing weight 
        proportionally among the active modalities.
        
        Args:
            modality_scores: e.g. {"image": 0.8, "text": 0.4, "pdf": None, "sensor": 0.2}
            
        Returns:
            Dictionary containing global_score and risk_level.
        """
        active_weights_sum = 0.0
        weighted_score_sum = 0.0
        
        for modality, score in modality_scores.items():
            if score is not None and modality in self.base_weights:
                weight = self.base_weights[modality]
                active_weights_sum += weight
                weighted_score_sum += (score * weight)
                
        if active_weights_sum == 0.0:
            global_score = 0.0
        else:
            # Weighted average formula
            global_score = weighted_score_sum / active_weights_sum
            
        # Determine Risk Level based on thresholds
        if global_score < 0.35:
            risk_level = RiskLevel.normal
        elif global_score < 0.65:
            risk_level = RiskLevel.surveiller
        else:
            risk_level = RiskLevel.urgent
            
        return {
            "global_score": round(global_score, 4),
            "risk_level": risk_level,
            "active_weights_sum": round(active_weights_sum, 4)
        }

fusion_service = FusionService()
