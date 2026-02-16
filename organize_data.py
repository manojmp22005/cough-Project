import os
import shutil

# Paths
SOURCE_DIR = r"d:\cough-project-1\ESC-50-master\audio"
DEST_DIR = r"d:\cough-project-1\training_data"
COUGH_DIR = os.path.join(DEST_DIR, "cough")
NOISE_DIR = os.path.join(DEST_DIR, "noise")

# Ensure destination exists
os.makedirs(COUGH_DIR, exist_ok=True)
os.makedirs(NOISE_DIR, exist_ok=True)

# Process files
files = os.listdir(SOURCE_DIR)
count_cough = 0
count_noise = 0

print("Processing ESC-50 dataset...")

for f in files:
    if not f.endswith(".wav"):
        continue
        
    # ESC-50 format: {fold}-{clip_id}-{take}-{category_id}.wav
    # Category 24 is "Coughing"
    parts = f.split("-")
    category = parts[-1].replace(".wav", "")
    
    src = os.path.join(SOURCE_dir, f)
    
    if category == "24":
        dst = os.path.join(COUGH_DIR, f)
        shutil.copy2(src, dst)
        count_cough += 1
    else:
        # We limit noise to ~50 files to balance the dataset (ESC-50 has 40 coughs)
        # Using Category 0 (Dog) and 1 (Rooster) and 2 (Rain) for variety
        if count_noise < 50: 
            dst = os.path.join(NOISE_DIR, f)
            shutil.copy2(src, dst)
            count_noise += 1

print(f"Done! Copied {count_cough} Cough files and {count_noise} Noise files.")
print(f"Data is ready in: {DEST_DIR}")
