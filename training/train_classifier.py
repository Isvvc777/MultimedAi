from ultralytics import YOLO
import multiprocessing

def main():
    # 1. Load a pretrained YOLOv8 medium CLASSIFIER model
    model = YOLO("yolov8m-cls.pt") 

    # 2. Train exclusively on the HAM10000 dataset folder structure
    # The folder structure is simply train/class_name and val/class_name
    results = model.train(
        data=r"C:\MultimedAi\training\classifier_dataset", 
        epochs=300,            
        patience=20,           
        imgsz=224,             # Standard size for classification
        batch=16,              # Can use larger batches for classification
        workers=2,
        device=0,              
        name="production_skin_classifier", 
        optimizer="auto",      
        augment=True,          
        degrees=15.0,          # Rotate lesions
        flipud=0.5,            
        fliplr=0.5,            
    )

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
