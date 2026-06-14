from ultralytics import YOLO

def main():
    # Load the base YOLOv8 nano model
    model = YOLO("yolov8n.pt") 

    # Start training on our freshly merged dataset!
    # Because we are doing a lot of classes and the dataset is decently sized,
    # we'll train for 50 epochs.
    results = model.train(
        data=r"C:\MultimedAi\training\merged_dataset\data.yaml", 
        epochs=50,       
        imgsz=640,       
        batch=16,        
        device=0,        # Use GPU 0. Change to 'cpu' if no Nvidia GPU is available
        name="multimedai_yolo", # The weights will be saved in runs/detect/multimedai_yolo/weights/best.pt
        patience=10      # Early stopping if no improvement for 10 epochs
    )

if __name__ == '__main__':
    # Fix for potential multiprocessing issues on Windows
    import multiprocessing
    multiprocessing.freeze_support()
    main()
