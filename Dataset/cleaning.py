import os
import zipfile
import glob
import hashlib
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import cv2
from collections import Counter
from tqdm import tqdm

# ======================================================
# 1. CONFIGURATION
# ======================================================
ZIP_FILENAME = 'KitchenHygiene.v1i.yolov8.zip'

# Explicit Class Names from your data.yaml
CLASS_NAMES = {
    0: 'apron',
    1: 'cockroach',
    2: 'gloves',
    3: 'hairnet',
    4: 'lizard',
    5: 'no_apron',
    6: 'no_gloves',
    7: 'no_hairnet',
    8: 'rat'
}

# ======================================================
# 2. AUTO-EXTRACTION
# ======================================================
extract_dir = "eda_workspace"

if not os.path.exists(ZIP_FILENAME):
    print(f"❌ Error: File '{ZIP_FILENAME}' not found. Please upload it.")
else:
    # Clean previous run
    if os.path.exists(extract_dir):
        import shutil
        shutil.rmtree(extract_dir)

    print(f"📂 Extracting {ZIP_FILENAME}...")
    with zipfile.ZipFile(ZIP_FILENAME, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

# ======================================================
# 3. DEEP SCANNING (MD5 + METRICS)
# ======================================================
print("\n🔍 Scanning images & calculating deep metrics...")

image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
all_image_paths = []
for ext in image_extensions:
    all_image_paths.extend(glob.glob(f"{extract_dir}/**/{ext}", recursive=True))

# Tracking Structures
unique_hashes = {}
image_status = {}  # 'Unique' or 'Duplicate'
duplicate_count = 0
valid_unique_count = 0

# Deep Metrics Storage
brightness_vals = []
resolutions = []
objects_per_image = []

for img_path in tqdm(all_image_paths, desc="Processing Images"):
    # A. Duplicate Check
    try:
        with open(img_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        if file_hash in unique_hashes:
            image_status[img_path] = 'Duplicate'
            duplicate_count += 1
            # Skip deep metrics for duplicates to avoid skewing data
        else:
            unique_hashes[file_hash] = img_path
            image_status[img_path] = 'Unique'
            valid_unique_count += 1

            # B. Deep Image Metrics (Resolution & Brightness)
            img = cv2.imread(img_path)
            if img is not None:
                h, w, _ = img.shape
                resolutions.append(f"{w}x{h}")
                # Average pixel intensity (0=Dark, 255=Bright)
                brightness_vals.append(np.mean(img))

    except Exception as e:
        print(f"⚠️ Read Error: {e}")

# ======================================================
# 4. LABEL PARSING & COUNTING
# ======================================================
print("\n📝 Parsing labels...")

counts_unique = Counter()
counts_duplicates = Counter()
missing_labels = 0

for img_path in tqdm(all_image_paths, desc="Parsing Labels"):
    status = image_status.get(img_path)
    if not status: continue

    # Infer Label Path
    base_name = os.path.splitext(os.path.basename(img_path))[0]
    parent_dir = os.path.dirname(img_path)

    # Check parallel 'labels' folder first (Standard YOLO)
    if 'images' in parent_dir:
        label_dir = parent_dir.replace('images', 'labels')
        label_path = os.path.join(label_dir, base_name + ".txt")
    else:
        # Check same folder
        label_path = os.path.join(parent_dir, base_name + ".txt")

    # Parse
    obj_count_in_this_img = 0
    if os.path.exists(label_path):
        try:
            with open(label_path, 'r') as f:
                lines = f.readlines()
                obj_count_in_this_img = len(lines)

                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 1:
                        class_id = int(parts[0])
                        if status == 'Unique':
                            counts_unique[class_id] += 1
                        else:
                            counts_duplicates[class_id] += 1
        except: pass
    else:
        missing_labels += 1

    if status == 'Unique':
        objects_per_image.append(obj_count_in_this_img)

# ======================================================
# 5. ANALYSIS & DATAFRAME
# ======================================================
data = []
total_unique_objects = sum(counts_unique.values())

for cls_id in CLASS_NAMES:
    cls_name = CLASS_NAMES[cls_id]
    u_count = counts_unique.get(cls_id, 0)
    d_count = counts_duplicates.get(cls_id, 0)
    pct = (u_count / total_unique_objects * 100) if total_unique_objects > 0 else 0

    data.append({
        'Class ID': cls_id, 'Class Name': cls_name,
        'Count (Unique)': u_count, 'Duplicates': d_count,
        'Percentage': pct
    })

df = pd.DataFrame(data).sort_values(by='Count (Unique)', ascending=False)

# Imbalance Logic
if not df.empty and total_unique_objects > 0:
    active = df[df['Count (Unique)'] > 0]
    if not active.empty:
        maj_row = active.iloc[0]
        min_row = active.iloc[-1]
        ratio = maj_row['Count (Unique)'] / min_row['Count (Unique)']
        status = "HIGH" if ratio > 3.0 else ("MODERATE" if ratio > 1.5 else "BALANCED")
        sugg = "Use 'mosaic=1.0' & 'mixup=0.1'" if ratio > 3.0 else "None"
    else:
        status, sugg, ratio = "EMPTY", "Check labels", 0
else:
    status, sugg, ratio = "ERROR", "No objects", 0

# ======================================================
# 6. FINAL REPORT
# ======================================================
print("\n" + "="*50)
print("       DATASET DIAGNOSTIC REPORT")
print("="*50)
print("1. HEALTH CHECK")
print(f"   - Total Images:      {len(all_image_paths)}")
print(f"   - Valid (Unique):    {valid_unique_count}")
print(f"   - Duplicates:        {duplicate_count} ({(duplicate_count/len(all_image_paths)*100):.1f}%)")
print(f"   - Missing Labels:    {missing_labels}")

print("\n2. DEEP STATS")
if resolutions:
    res_count = Counter(resolutions)
    common_res = res_count.most_common(1)[0]
    print(f"   - Most Common Res:   {common_res[0]} ({common_res[1]} images)")
    print(f"   - Avg Brightness:    {np.mean(brightness_vals):.2f} (Target: ~100-150)")
    print(f"   - Avg Objects/Img:   {np.mean(objects_per_image):.2f}")

print("\n3. IMBALANCE ANALYSIS")
if not df.empty:
    print(f"   📉 Minority Class: '{min_row['Class Name']}' ({min_row['Count (Unique)']})")
    print(f"   📈 Majority Class: '{maj_row['Class Name']}' ({maj_row['Count (Unique)']})")
    print(f"   ⚖️ Imbalance Ratio: 1 : {ratio:.2f}")
    print(f"   ⚠️ STATUS: {status}. Suggestion: {sugg}")

print("\n4. DETAILED STATS")
print(f" {'ID':<3} | {'Class Name':<15} | {'Unique':<8} | {'Dups':<6} | {'%':<6}")
print("-" * 50)
for _, row in df.iterrows():
    print(f" {row['Class ID']:<3} | {row['Class Name']:<15} | {row['Count (Unique)']:<8} | {row['Duplicates']:<6} | {row['Percentage']:.1f}%")

# ======================================================
# 7. VISUALIZATION
# ======================================================
sns.set_style("whitegrid")
plt.figure(figsize=(18, 5))

# Plot 1: Class Distribution
plt.subplot(1, 3, 1)
avg_c = df['Count (Unique)'].mean()
cols = ['#2ecc71' if x >= avg_c else '#e74c3c' for x in df['Count (Unique)']]
sns.barplot(data=df, x='Class Name', y='Count (Unique)', palette=cols)
plt.axhline(avg_c, color='gray', linestyle='--', label='Avg')
plt.xticks(rotation=45, ha='right')
plt.title("Class Distribution (Unique)")
plt.legend()

# Plot 2: Brightness Distribution
plt.subplot(1, 3, 2)
sns.histplot(brightness_vals, kde=True, color='orange', bins=30)
plt.axvline(np.mean(brightness_vals), color='red', linestyle='--')
plt.title("Image Brightness (Lighting Check)")
plt.xlabel("Pixel Intensity (0-255)")

# Plot 3: Object Density
plt.subplot(1, 3, 3)
sns.histplot(objects_per_image, discrete=True, color='purple')
plt.title("Objects per Image (Density)")
plt.xlabel("Count of Objects")

plt.tight_layout()
plt.show()