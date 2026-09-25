"""
Phase 5 Verification: TEST 8 (LangGraph Runtime Proof) & TEST 9 (Database Persistence Across Backend Restart)
"""

import os
import sys
import time
import subprocess
import requests

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from graph.workflow import get_kisansaarthi_graph


def test_08_langgraph_runtime_proof():
    print("\n--------------------------------------------------------------------------------")
    print("EXECUTING TEST 8: LangGraph Runtime Execution Proof")
    print("--------------------------------------------------------------------------------")

    graph = get_kisansaarthi_graph()
    
    # Verify graph node topology
    node_keys = list(graph.nodes.keys())
    print(f"Compiled LangGraph Nodes: {node_keys}")
    assert "supervisor" in node_keys
    assert "tractor_node" in node_keys
    assert "crop_health_node" in node_keys
    assert "insurance_node" in node_keys
    assert "general_agri_node" in node_keys
    assert "crop_residue_node" in node_keys
    assert "post_processor" in node_keys

    # Trace execution of a real state payload
    stream_chunks = list(graph.stream({
        "farmer_id": "test_proof_farmer",
        "conversation_id": "test_proof_cid",
        "language": "en",
        "user_message": "I need a tractor",
        "crop_name": None,
    }))
    
    step_sequence = [list(chunk.keys())[0] for chunk in stream_chunks]
    full_trace = ["START"] + step_sequence + ["END"]
    trace_str = " -> ".join(full_trace)
    print(f"Runtime Execution Trace: {trace_str}")

    # Validate exact path
    assert full_trace == ["START", "supervisor", "tractor_node", "post_processor", "END"], \
        f"Unexpected execution trace: {full_trace}"

    print("[PASS] TEST 8: LangGraph Runtime Proof Verified!")
    print(f"       Trace: {trace_str}")
    return True


def test_09_database_persistence_across_restart():
    print("\n--------------------------------------------------------------------------------")
    print("EXECUTING TEST 9: Database Persistence Across Backend Restart")
    print("--------------------------------------------------------------------------------")

    fid = f"farmer_persist_{int(time.time())}"
    cid = f"conv_persist_{int(time.time())}"

    # Step A: Send request to create a real record in SQLite via POST /api/chat
    chat_url = "http://127.0.0.1:8000/api/chat"
    r = requests.post(chat_url, json={
        "farmer_id": fid,
        "conversation_id": cid,
        "language": "en",
        "message": "I need a tractor in Miryalaguda tomorrow at 10 AM",
    }, timeout=10)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    resp_data = r.json()
    print(f"Created initial record via LangGraph API. Status: {resp_data.get('status')}")

    # Verify record exists in SQLite via /api/requests
    req_url = f"http://127.0.0.1:8000/api/requests?farmer_id={fid}"
    r_before = requests.get(req_url, timeout=10).json()
    assert len(r_before) > 0, "No records returned before restart"
    record_id = r_before[0]["id"]
    print(f"Record verified in SQLite before restart: ID={record_id}, Type={r_before[0]['type']}")

    # Step B: Restart backend uvicorn process
    print("Restarting FastAPI Uvicorn backend...")
    # Find listening process on 8000
    find_cmd = "powershell -Command \"(Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue).OwningProcess\""
    pid_out = subprocess.check_output(find_cmd, shell=True).decode().strip()
    pids = [p.strip() for p in pid_out.splitlines() if p.strip().isdigit()]
    for p in pids:
        print(f"Terminating uvicorn PID: {p}")
        subprocess.run(f"taskkill /F /PID {p}", shell=True, capture_output=True)

    time.sleep(2)

    # Spawn fresh uvicorn process
    py_exe = sys.executable
    print(f"Spawning fresh backend process with {py_exe}...")
    proc = subprocess.Popen(
        [py_exe, "-m", "uvicorn", "main:app", "--port", "8000"],
        cwd=backend_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"New uvicorn process started (PID: {proc.pid}). Waiting for health...")

    # Wait for server to become responsive
    healthy = False
    for _ in range(30):
        time.sleep(1)
        try:
            health_res = requests.get("http://127.0.0.1:8000/health", timeout=2)
            if health_res.status_code == 200:
                healthy = True
                break
        except Exception:
            pass

    assert healthy, "Backend failed to restart within 30 seconds"
    print("Backend restarted successfully and responded to /health!")

    # Step C: Query /api/requests after restart
    r_after = requests.get(req_url, timeout=10).json()
    assert len(r_after) > 0, "Records disappeared after restart!"
    after_record_id = r_after[0]["id"]
    print(f"Record verified in SQLite after restart: ID={after_record_id}")
    assert after_record_id == record_id, f"Record ID mismatch: expected {record_id}, got {after_record_id}"

    print("[PASS] TEST 9: Database Persistence Across Restart Verified!")
    print(f"       Persisted Record ID: {after_record_id}")
    return True


if __name__ == "__main__":
    t8_pass = test_08_langgraph_runtime_proof()
    t9_pass = test_09_database_persistence_across_restart()
    print("\n================================================================================")
    print(f"TEST 8 (Runtime Proof): {'PASS' if t8_pass else 'FAIL'}")
    print(f"TEST 9 (Restart Persistence): {'PASS' if t9_pass else 'FAIL'}")
    print("================================================================================")
