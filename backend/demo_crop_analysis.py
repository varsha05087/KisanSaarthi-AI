import json
import os
import sys
import urllib.request
import uuid

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:8000/api"


def test_real_crop_image(image_path: str, fields: dict):
    boundary = f"----WebKitBoundary{uuid.uuid4().hex}"
    body = bytearray()

    for k, v in fields.items():
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode("utf-8"))
        body.extend(f"{v}\r\n".encode("utf-8"))

    with open(image_path, "rb") as f:
        file_bytes = f.read()

    filename = os.path.basename(image_path)
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'.encode("utf-8"))
    body.extend(b"Content-Type: image/jpeg\r\n\r\n")
    body.extend(file_bytes)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        f"{BASE_URL}/crop/health",
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


if __name__ == "__main__":
    img = os.path.join(os.path.dirname(__file__), "data", "samples", "tomato_leaf_blight.jpg")
    res = test_real_crop_image(img, {"farmer_id": "F001", "crop_name": "Tomato", "language": "en"})
    print("=== REAL CROP HEALTH RESPONSE (TOMATO - ENGLISH) ===")
    print(json.dumps(res, indent=2, ensure_ascii=False))
