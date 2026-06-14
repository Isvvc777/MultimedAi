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
WOUND_DIR = BASE_DIR / "wound.v4i.yolov8"

MERGED_DIR = Path(r"C:\MultimedAi\training\merged_dataset")

# 11 Classes total
WOUND_CLASSES = ['abrasions', 'bruises', 'cut', 'stab']
HAM_CLASSES = ['nv', 'mel', 'bkl', 'bcc', 'akiec', 'vasc', 'df']

CLASS_MAP = {}
for i, cls in enumerate(WOUND_CLASSES):
    CLASS_MAP[cls] = i
for i, cls in enumerate(HAM_CLASSES):
    CLASS_MAP[cls] = i + len(WOUND_CLASSES)

MAX_HAM_PER_CLASS = 600  # Prevent extreme imbalance against wound data

def setup_directories():
    if MERGED_DIR.exists():
        shutil.rmtree(MERGED_DIR)
    
    for split in ['train', 'valid']:
        (MERGED_DIR / split / 'images').mkdir(parents=True, exist_ok=True)
        (MERGED_DIR / split / 'labels').mkdir(parents=True, exist_ok=True)

def find_ham_image(image_id):
    filename = f"{image_id}.jpg"
    if (HAM_IMG_DIR_1 / filename).exists():
        return HAM_IMG_DIR_1 / filename
    if (HAM_IMG_DIR_2 / filename).exists():
        return HAM_IMG_DIR_2 / filename
    return None

def process_ham10000():
    print("Processing HAM10000...")
    # Read metadata and group by class
    class_images = {cls: [] for cls in HAM_CLASSES}
    
    with open(HAM_METADATA, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dx = row['dx']
            img_id = row['image_id']
            if dx in class_images:
                class_images[dx].append(img_id)
                
    # Sample and copy
    total_copied = 0
    for cls, images in class_images.items():
        # Shuffle and limit
        random.shuffle(images)
        sampled = images[:MAX_HAM_PER_CLASS]
        
        # Split 80/20 train/valid
        train_count = int(len(sampled) * 0.8)
        
        for idx, img_id in enumerate(sampled):
            split = 'train' if idx < train_count else 'valid'
            src_img = find_ham_image(img_id)
            
            if src_img:
                # Copy image
                dst_img = MERGED_DIR / split / 'images' / src_img.name
                shutil.copy2(src_img, dst_img)
                
                # Write dummy label (center 90%)
                label_txt = f"{CLASS_MAP[cls]} 0.5 0.5 0.9 0.9\n"
                dst_label = MERGED_DIR / split / 'labels' / f"{img_id}.txt"
                with open(dst_label, 'w') as lf:
                    lf.write(label_txt)
                
                total_copied += 1
                
        print(f"  Copied {len(sampled)} images for class '{cls}'")
        
    print(f"Done. Total HAM10000 images processed: {total_copied}")

def copy_wound_dataset():
    print("Copying Wound dataset...")
    # Check if wound dir exists
    if not WOUND_DIR.exists():
        print("Warning: Wound dataset not found.")
        return
        
    for split in ['train', 'valid']:
        src_split_dir = WOUND_DIR / split
        if not src_split_dir.exists():
            continue
            
        src_images = src_split_dir / 'images'
        src_labels = src_split_dir / 'labels'
        
        if not src_images.exists() or not src_labels.exists():
            continue
            
        # Copy images
        img_count = 0
        for img in src_images.iterdir():
            if img.is_file():
                shutil.copy2(img, MERGED_DIR / split / 'images' / img.name)
                img_count += 1
                
        # Copy labels (note: wound classes are 0-3, which perfectly matches our unified map)
        for lbl in src_labels.iterdir():
            if lbl.is_file():
                shutil.copy2(lbl, MERGED_DIR / split / 'labels' / lbl.name)
                
        print(f"  Copied {img_count} images for split '{split}'")

def write_yaml():
    yaml_path = MERGED_DIR / 'data.yaml'
    all_classes = WOUND_CLASSES + HAM_CLASSES
    
    yaml_content = f"""train: ./train/images
val: ./valid/images

nc: {len(all_classes)}
names: {all_classes}
"""
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    print("Generated data.yaml")

if __name__ == "__main__":
    random.seed(42)
    print(f"Starting merge process. Output directory: {MERGED_DIR}")
    setup_directories()
    process_ham10000()
    copy_wound_dataset()
    write_yaml()
    print("Merging complete!")
