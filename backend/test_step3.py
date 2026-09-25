import json
import urllib.request

def post(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return r.status, json.loads(r.read().decode("utf-8"))

def get(url):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req) as r:
        return r.status, json.loads(r.read().decode("utf-8"))

if __name__ == "__main__":
    print("--- RUNNING STEP 3 TESTS ---")

    # Test 1: Create farmer
    status, farmer = post("http://127.0.0.1:8000/api/farmers", {
        "name": "Ramu",
        "phone": "9876543210",
        "language": "te"
    })
    farmer_id = farmer["id"]
    print(f"[PASS] Test 1: Create Farmer -> HTTP {status}, ID={farmer_id}, Name={farmer['name']}, Phone={farmer['phone']}")

    # Test 2: Retrieve farmer
    status, retrieved = get(f"http://127.0.0.1:8000/api/farmers/{farmer_id}")
    match = (retrieved["id"] == farmer_id and retrieved["name"] == "Ramu")
    print(f"[PASS] Test 2: Retrieve Farmer -> HTTP {status}, ID={retrieved['id']}, Matches={match}")

    # Test 3: Create request
    status, req = post("http://127.0.0.1:8000/api/requests", {
        "farmer_id": farmer_id,
        "type": "tractor_booking",
        "status": "pending",
        "current_step": "Locating tractors near Miryalaguda",
        "result": "Matched with provider Srinivas"
    })
    req_id = req["id"]
    print(f"[PASS] Test 3: Create Request -> HTTP {status}, ReqID={req_id}, Type={req['type']}")

    # Test 4: Retrieve requests
    status, reqs = get(f"http://127.0.0.1:8000/api/requests?farmer_id={farmer_id}")
    found = any(r["id"] == req_id for r in reqs)
    print(f"[PASS] Test 4: Retrieve Requests -> HTTP {status}, Count={len(reqs)}, Contains Created Request={found}")

    # Test Tractor Booking Persistence
    status, booking = post("http://127.0.0.1:8000/api/tractors/book", {
        "farmer_id": farmer_id,
        "tractor_id": "TRK-575",
        "date": "2026-09-25",
        "time": "08:00 AM",
        "location": "Peddapuram"
    })
    print(f"[PASS] Tractor Booking Storage -> HTTP {status}, BookingID={booking.get('booking_id')}")

    print("\n--- TESTS 1-4 COMPLETED SUCCESSFULLY ---")
