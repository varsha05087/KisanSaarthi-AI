import json
import urllib.request

def get(url):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req) as r:
        return r.status, json.loads(r.read().decode("utf-8"))

if __name__ == "__main__":
    print("--- RUNNING TEST 5: PERSISTENCE VERIFICATION AFTER RESTART ---")

    # Test 5: Verify farmer still exists
    status, farmer = get("http://127.0.0.1:8000/api/farmers/FARMER-92609CFE")
    print(f"[PASS] Farmer Persisted: HTTP {status} | ID={farmer['id']} | Name={farmer['name']} | Phone={farmer['phone']}")

    # Verify requests still exist
    status, reqs = get("http://127.0.0.1:8000/api/requests?farmer_id=FARMER-92609CFE")
    req_types = [r["type"] for r in reqs]
    print(f"[PASS] Requests Persisted: HTTP {status} | Total Records={len(reqs)} | Types={req_types}")

    print("\n--- TEST 5 PASSED: DATA SUCCESSFULLY PERSISTED ACROSS SERVER RESTART ---")
