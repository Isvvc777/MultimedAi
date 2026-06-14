import os
import shutil
import random
import csv
from pathlib import Path

# Paths
BASE_DIR = Path(r"C:\MultimedAi\training\dataset")
HAM_METADATA = BASE_DIR / "HAM10000_metadata.csv"
HAM_IMG_DIR_1 = BASE_DIR / "HAM10000_images_part_1"
HAM_IMG_DIR_2 = BASE_DIR / "HAM10000_images_part_2"

# Output classification dataset directory
CLS_DIR = Path(r"C:\MultimedAi\training\classifier_dataset")

HAM_CLASSES = ['nv', 'mel', 'bkl', 'bcc', 'akiec', 'vasc', 'df']

def setup_directories():
    if CLS_DIR.exists():
        shutil.rmtree(CLS_DIR)
        
    for split in ['train', 'val']:
        for cls in HAM_CLASSES:
            (CLS_DIR / split / cls).mkdir(parents=True, exist_ok=True)

def find_ham_image(image_id):
    filename = f"{image_id}.jpg"
    if (HAM_IMG_DIR_1 / filename).exists():
        return HAM_IMG_DIR_1 / filename
    if (HAM_IMG_DIR_2 / filename).exists():
        return HAM_IMG_DIR_2 / filename
    return None

def prepare_data():
    print("Preparing HAM10000 Classification Dataset...")
    class_images = {cls: [] for cls in HAM_CLASSES}
    
    with open(HAM_METADATA, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dx = row['dx']
            img_id = row['image_id']
            if dx in class_images:
                class_images[dx].append(img_id)
                
    total_copied = 0
    # For classification, we want to cap heavily overrepresented classes (nv) 
    # but keep all images for underrepresented ones
    MAX_PER_CLASS = 1500 
    
    for cls, images in class_images.items():
        random.shuffle(images)
        sampled = images[:MAX_PER_CLASS]
        
        train_count = int(len(sampled) * 0.8)
        
        for idx, img_id in enumerate(sampled):
            split = 'train' if idx < train_count else 'val'
            src_img = find_ham_image(img_id)
            
            if src_img:
                dst_img = CLS_DIR / split / cls / src_img.name
                shutil.copy2(src_img, dst_img)
                total_copied += 1
                
        print(f"  Copied {len(sampled)} images for class '{cls}'")
        
    print(f"Done! Created classification dataset with {total_copied} total images.")

if __name__ == "__main__":
    random.seed(42)
    setup_directories()
    prepare_data()
