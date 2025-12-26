import requests
import json
import time

BASE_URL = "http://localhost:8000"
USER_EMAIL = "tester@example.com"
USER_PASS = "testpassword123"

def test_auth():
    print("\n--- Testing Authentication ---")
    # 1. Register
    reg_data = {
        "email": USER_EMAIL,
        "username": "tester",
        "password": USER_PASS
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=reg_data)
    print(f"Register: {response.status_code}")
    
    # 2. Login
    login_data = {
        "username": USER_EMAIL, # auth uses email as username in form
        "password": USER_PASS
    }
    # Note: Using json here instead of form-data for testing simplicity, 
    # but the actual endpoint expects OAuth2PasswordRequestForm.
    # We should use OAuth2 compatible login.
    response = requests.post(f"{BASE_URL}/api/auth/login", data={"username": USER_EMAIL, "password": USER_PASS})
    print(f"Login: {response.status_code}")
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("Token acquired.")
        return token
    return None

def test_youtube(token):
    print("\n--- Testing YouTube ---")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/youtube/auth-url", headers=headers)
    print(f"Auth URL Endpoint: {response.status_code}")
    if response.status_code == 200:
        print(f"URL: {response.json().get('url')[:50]}...")

def test_workflow(token):
    print("\n--- Testing Workflow ---")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create Column
    col_response = requests.post(f"{BASE_URL}/api/workflow/columns?name=Ideas&order=1", headers=headers)
    print(f"Create Column: {col_response.status_code}")
    if col_response.status_code == 200:
        col_id = col_response.json()["id"]
        # Create Card
        card_data = {"title": "Test Video Idea", "description": "AI script test", "column_id": col_id}
        card_response = requests.post(f"{BASE_URL}/api/workflow/cards", json=card_data, headers=headers)
        print(f"Create Card: {card_response.status_code}")

def test_analytics(token):
    print("\n--- Testing Analytics ---")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/analytics/summary", headers=headers)
    print(f"Summary: {response.status_code}")
    if response.status_code == 200:
        print(f"Stats: {response.json()}")

def main():
    print("🚀 Starting API Verification...")
    token = test_auth()
    if token:
        test_youtube(token)
        test_workflow(token)
        test_analytics(token)
    else:
        print("❌ Auth failed, skipping other tests.")

if __name__ == "__main__":
    main()
