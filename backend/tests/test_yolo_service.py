import pytest
from PIL import Image
from app.services.yolo_service import yolo_service

@pytest.mark.asyncio
async def test_yolo_service_analyze():
    # Create a dummy blank image for testing
    # Note: A blank image might not yield detections, so we mainly test the return types
    img = Image.new('RGB', (640, 640), color='white')
    
    detections, risk_score = await yolo_service.analyze_image(img)
    
    assert isinstance(detections, list)
    assert isinstance(risk_score, float)
    assert 0.0 <= risk_score <= 1.0
