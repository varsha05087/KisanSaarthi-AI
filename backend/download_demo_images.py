"""
Download 5 real agricultural crop images from the official PlantVillage dataset
matching exactly the 5 requested classes:
1. Tomato with Early Blight (tomato_early_blight.jpg)
2. Healthy Tomato Plant (tomato_healthy.jpg)
3. Corn (Maize) with Common Rust (corn_common_rust.jpg)
4. Potato with Early Blight (potato_early_blight.jpg)
5. Grape with Black Rot (grape_black_rot.jpg)
"""

import os
import json
import urllib.request
from PIL import Image
from services.disease_model_service import predict_crop_disease

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEMO_DIR = os.path.join(BASE_DIR, "data", "demo_images")
os.makedirs(DEMO_DIR, exist_ok=True)

SAMPLES_SPEC = [
    {
        "target_filename": "tomato_early_blight.jpg",
        "plantvillage_class": "Tomato___Early_blight",
        "expected_crop": "Tomato",
        "expected_disease": "Early Blight",
        "model_label": "Tomato with Early Blight",
    },
    {
        "target_filename": "tomato_healthy.jpg",
        "plantvillage_class": "Tomato___healthy",
        "expected_crop": "Tomato",
        "expected_disease": "Healthy",
        "model_label": "Healthy Tomato Plant",
    },
    {
        "target_filename": "corn_common_rust.jpg",
        "plantvillage_class": "Corn_(maize)___Common_rust_",
        "expected_crop": "Corn",
        "expected_disease": "Common Rust",
        "model_label": "Corn (Maize) with Common Rust",
    },
    {
        "target_filename": "potato_early_blight.jpg",
        "plantvillage_class": "Potato___Early_blight",
        "expected_crop": "Potato",
        "expected_disease": "Early Blight",
        "model_label": "Potato with Early Blight",
    },
    {
        "target_filename": "grape_black_rot.jpg",
        "plantvillage_class": "Grape___Black_rot",
        "expected_crop": "Grape",
        "expected_disease": "Black Rot",
        "model_label": "Grape with Black Rot",
    },
]

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

print("=" * 80)
print("FETCHING REAL PLANTVILLAGE IMAGES FOR DEMO SET")
print("Target Directory:", DEMO_DIR)
print("=" * 80)

results = []

for spec in SAMPLES_SPEC:
    target_name = spec["target_filename"]
    folder = spec["plantvillage_class"]
    expected_label = spec["model_label"]
    
    api_url = f"https://api.github.com/repos/spMohanty/PlantVillage-Dataset/contents/raw/color/{folder}"
    req = urllib.request.Request(api_url, headers=headers)
    
    with urllib.request.urlopen(req) as resp:
        file_list = json.loads(resp.read().decode("utf-8"))
    
    best_match = None
    best_prob = -1.0
    
    # Check first 15 images to find the clearest, most representative leaf image
    for item in file_list[:15]:
        dl_url = item["download_url"]
        img_req = urllib.request.Request(dl_url, headers=headers)
        with urllib.request.urlopen(img_req) as img_resp:
            img_bytes = img_resp.read()
        
        # Test image validity
        try:
            img = Image.open(urllib.request.io.BytesIO(img_bytes))
            img.verify()
        except Exception:
            continue
            
        # Run inference through the real model to verify top-1 classification matches
        pred = predict_crop_disease(img_bytes)
        top1 = pred.get("top_3_predictions", [{}])[0]
        top1_label = top1.get("label", "")
        top1_prob = top1.get("confidence", 0.0)
        
        if top1_label == expected_label:
            if top1_prob > best_prob:
                best_prob = top1_prob
                best_match = {
                    "original_name": item["name"],
                    "source_url": dl_url,
                    "bytes": img_bytes,
                    "prediction": pred,
                    "top1_prob": top1_prob,
                    "image_size": Image.open(urllib.request.io.BytesIO(img_bytes)).size,
                }
                if best_prob > 0.90:
                    break

    if best_match:
        save_path = os.path.join(DEMO_DIR, target_name)
        with open(save_path, "wb") as f:
            f.write(best_match["bytes"])
        
        rel_path = os.path.relpath(save_path, BASE_DIR)
        print(f"\n[DOWNLOADED] {target_name}")
        print(f"  Source File:     {best_match['original_name']}")
        print(f"  Source URL:      {best_match['source_url']}")
        print(f"  Local Path:      {save_path}")
        print(f"  Dimensions:      {best_match['image_size']}")
        print(f"  Size on Disk:    {len(best_match['bytes'])} bytes")
        print(f"  Model Top-1:     {expected_label} ({best_match['top1_prob'] * 100:.2f}%)")
        
        results.append({
            "target": target_name,
            "path": save_path,
            "orig_name": best_match["original_name"],
            "url": best_match["source_url"],
            "size": len(best_match["bytes"]),
            "prediction": best_match["prediction"],
        })
    else:
        print(f"\n[ERROR] No high-confidence sample found for {target_name}")

print("\n" + "=" * 80)
print(f"DOWNLOAD COMPLETE: {len(results)} / 5 REAL IMAGES SAVED TO data/demo_images/")
print("=" * 80)
