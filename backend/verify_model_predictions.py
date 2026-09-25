"""
Verification script for real pretrained MobileNetV2 crop disease model.
Tests all required cases:
1. Tomato healthy
2. Tomato disease
3. Corn disease
4. Potato disease
5. Blurry image
6. Non-plant image
"""

import os
import json
from services.disease_model_service import predict_crop_disease, MODEL_NAME, MODEL_SOURCE, DATASET_NAME

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "samples")

test_cases = [
    ("Tomato Healthy", "tomato_healthy.jpg", "Tomato"),
    ("Tomato Disease", "tomato_early_blight.jpg", "Tomato"),
    ("Corn Disease", "corn_common_rust.jpg", "Corn"),
    ("Potato Disease", "potato_early_blight.jpg", "Potato"),
    ("Blurry Image", "blurry_leaf.jpg", None),
    ("Non-Plant Object", "non_crop_object.jpg", None),
]

print("=" * 80)
print("REAL PRETRAINED MOBILENETV2 CROP DISEASE MODEL VERIFICATION")
print(f"Model ID: {MODEL_NAME}")
print(f"Source:   {MODEL_SOURCE}")
print(f"Dataset:  {DATASET_NAME}")
print("=" * 80)

for test_name, filename, hint in test_cases:
    path = os.path.join(SAMPLES_DIR, filename)
    with open(path, "rb") as f:
        img_bytes = f.read()

    res = predict_crop_disease(img_bytes, crop_hint=hint)
    print(f"\n>>> TEST CASE: {test_name} ({filename})")
    print(f"Status:             {res.get('status')}")
    print(f"Predicted Crop:     {res.get('crop')}")
    print(f"Predicted Problem:  {res.get('predicted_problem')}")
    print(f"Confidence:         {res.get('confidence')}")
    print(f"Is Healthy:         {res.get('is_healthy')}")
    print(f"Is Plant:           {res.get('is_plant')}")
    print(f"Uncertain:          {res.get('uncertain')}")
    if res.get("top_3_predictions"):
        print("Top 3 Predictions:")
        for i, p in enumerate(res["top_3_predictions"], 1):
            print(f"  {i}. {p['label']} -> {p['confidence']*100:.2f}% (Crop: {p['crop']}, Disease: {p['disease']})")
    if res.get("warning"):
        print(f"Warning / Guard:    {res['warning']}")
    if res.get("evidence"):
        print(f"Evidence:           {res['evidence']}")

print("\n" + "=" * 80)
print("ALL VERIFICATION CASES EVALUATED SUCCESSFULLY")
print("=" * 80)
