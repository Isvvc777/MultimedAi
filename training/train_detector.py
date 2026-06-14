from ultralytics import YOLO
import multiprocessing

def main():
    # 1. Load a pretrained YOLOv8 medium model for detection
    model = YOLO("yolov8m.pt") 

    # 2. Train exclusively on the wound dataset
    # We use high epochs and strong data augmentation to get production-level accuracy
    results = model.train(
        data=r"C:\MultimedAi\training\dataset\wound.v4i.yolov8\data.yaml", 
        epochs=300,            # Max epochs for production
        patience=25,           # Stop early if no improvement for 25 epochs
        imgsz=640,             
        batch=8,              
        workers=2,
        device=0,              
        name="production_wound_detector", 
        optimizer="auto",      
        lr0=0.01,              # Initial learning rate
        augment=True,          # Enable strong augmentation
        flipud=0.5,            # Up-down flip probability
        fliplr=0.5,            # Left-right flip probability
        mosaic=1.0,            # Mosaic augmentation (great for small wounds)
    )

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
