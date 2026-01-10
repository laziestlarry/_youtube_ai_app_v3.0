import requests
import json

BASE_URL = "http://localhost:8000"

def test_dashboard_api():
    print(f"Testing API at {BASE_URL}...")
    
    # 1. Login
    login_data = {
        "username": "admin@example.com",
        "password": "admin123"
    }
    
    print("\n[1] Logging in...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        token = response.json()["access_token"]
        print("✅ Login successful")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        if 'response' in locals():
            print(f"Response: {response.text}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test Analytics Summary
    print("\n[2] Testing /api/analytics/summary...")
    try:
        response = requests.get(f"{BASE_URL}/api/analytics/summary", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Data: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Summary failed: {e}")
        if 'response' in locals():
            print(f"Response: {response.text}")

    # 3. Test Performance Metrics
    print("\n[3] Testing /api/analytics/performance-metrics...")
    try:
        response = requests.get(f"{BASE_URL}/api/analytics/performance-metrics", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Data: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Performance failed: {e}")
        if 'response' in locals():
            print(f"Response: {response.text}")

    # 4. Test Ignite Revenue Stats
    print("\n[4] Testing /api/agency/revenue-stats...")
    try:
        response = requests.get(f"{BASE_URL}/api/agency/revenue-stats", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Data: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Revenue Stats failed: {e}")
        if 'response' in locals():
            print(f"Response: {response.text}")

if __name__ == "__main__":
    test_dashboard_api()
