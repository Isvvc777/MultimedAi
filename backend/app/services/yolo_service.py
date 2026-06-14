import asyncio
from PIL import Image
from ultralytics import YOLO
from typing import List, Dict, Any, Tuple
from app.config import settings
import os

class VisionService:
    def __init__(self):
        # We will look for our production models in the weights folder.
        # If they haven't finished training yet, we gracefully fall back to the nano model.
        detector_path = os.path.join("app", "models", "weights", "detector_best.pt")
        classifier_path = os.path.join("app", "models", "weights", "classifier_best.pt")
        
        self.use_two_stage = os.path.exists(detector_path) and os.path.exists(classifier_path)
        
        if self.use_two_stage:
            print("Loading Production Two-Stage Vision Pipeline...")
            self.detector = YOLO(detector_path)
            self.classifier = YOLO(classifier_path)
        else:
            print("Production weights not found. Falling back to base YOLOv8n.")
            self.detector = YOLO("yolov8n.pt")
            self.classifier = None
            
        # Target classes to determine high risk
        self.wound_classes = ["abrasions", "bruises", "cut", "stab"]
        self.skin_disease_classes = ["mel", "bcc", "akiec"] # High risk skin diseases
        
    async def analyze_image(self, image: Image.Image) -> Tuple[List[Dict[str, Any]], float]:
        """
        Analyzes a PIL Image using the Two-Stage pipeline if available.
        Returns a tuple of (detections, risk_score).
        """
        def _analyze():
            detections = []
            max_risk = 0.0
            
            # STAGE 1: Detection (Wounds & Trauma)
            det_results = self.detector(image, conf=settings.yolo_confidence_threshold)
            
            for result in det_results:
                for box in result.boxes:
                    cls_id = int(box.cls[0].item())
                    conf = float(box.conf[0].item())
                    label = result.names[cls_id]
                    
                    risk = conf if label in self.wound_classes else conf * 0.2
                    if risk > max_risk:
                        max_risk = risk
                        
                    detections.append({
                        "label": label,
                        "confidence": conf,
                        "bbox": box.xyxy[0].tolist(),
                        "risk_contribution": risk
                    })
            
            # STAGE 2: Classification (Skin Diseases)
            if self.classifier:
                cls_results = self.classifier(image)
                # For classification, we look at the top prediction
                for result in cls_results:
                    top_idx = result.probs.top1
                    top_conf = float(result.probs.top1conf)
                    top_label = result.names[top_idx]
                    
                    # If the AI is highly confident it's a skin disease
                    if top_conf > 0.4:
                        risk = top_conf if top_label in self.skin_disease_classes else top_conf * 0.3
                        if risk > max_risk:
                            max_risk = risk
                            
                        # Add as a full-image detection
                        detections.append({
                            "label": top_label,
                            "confidence": top_conf,
                            "bbox": None, # No bounding box for whole-image classification
                            "risk_contribution": risk
                        })
            
            return detections, max_risk
            
        return await asyncio.to_thread(_analyze)

# Keep the same variable name so we don't break existing routes
yolo_service = VisionService()
