"""
Evaluation of the 5 real demo images through KisanSaarthi Crop Disease Model.
"""

import os
import json
from services.disease_model_service import predict_crop_disease

DEMO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "demo_images")
files = [
    "tomato_early_blight.jpg",
    "tomato_healthy.jpg",
    "corn_common_rust.jpg",
    "potato_early_blight.jpg",
    "grape_black_rot.jpg",
]

print("=" * 80)
print("EVALUATION OF REAL DEMO IMAGES THROUGH CROP DISEASE MODEL")
print("=" * 80)

for f in files:
    path = os.path.join(DEMO_DIR, f)
    with open(path, "rb") as fp:
        b = fp.read()
    res = predict_crop_disease(b)
    print(f"\nFile: {f} ({os.path.getsize(path)} bytes)")
    print(f"  Status:             {res.get('status')}")
    print(f"  Crop:               {res.get('crop')}")
    print(f"  Condition:          {res.get('predicted_problem')}")
    print(f"  Is Healthy:         {res.get('is_healthy')}")
    print(f"  Calibrated Conf:    {res.get('confidence')}")
    print("  Top-3 Softmax Distribution:")
    for p in res.get("top_3_predictions", []):
        print(f"    * Class {p['class_index']}: {p['label']} -> {p['confidence']*100:.2f}%")
