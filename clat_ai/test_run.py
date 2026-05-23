import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    print("\n[TEST] Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Body: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")

def test_chat_teach():
    print("\n[TEST] Manual Mode: Teach...")
    payload = {
        "mode": "teach",
        "topic": "Contract Law"
    }
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json().get('response')[:200]}...")
    except Exception as e:
        print(f"Teach test failed: {e}")

def test_auto_session():
    print("\n[TEST] Autonomous Mode: Session (2 cycles)...")
    payload = {
        "cycles": 2
    }
    try:
        response = requests.post(f"{BASE_URL}/auto", json=payload)
        print(f"Status: {response.status_code}")
        output = response.json().get("session_output", [])
        for step in output:
            print(f"\n--- STEP {step['step']} ---")
            print(f"Decision: {step['action']} on {step['topic']}")
            print(f"Reason: {step['reason']}")
            print(f"Output Preview: {step['output'][:100]}...")
    except Exception as e:
        print(f"Auto session failed: {e}")

if __name__ == "__main__":
    print("Waiting for server to be ready...")
    time.sleep(5)
    test_health()
    test_chat_teach()
    test_auto_session()
