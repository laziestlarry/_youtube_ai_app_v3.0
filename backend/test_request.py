import requests
import json

def test_initialize():
    url = "http://localhost:8000/api/initialize"
    data = {
        "channel_id": "test_channel",
        "api_key": "test_key",
        "preferences": {}
    }
    
    print("Sending request to:", url)
    print("Request data:", json.dumps(data, indent=2))
    
    try:
        response = requests.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print("\nResponse status:", response.status_code)
        print("Response headers:", dict(response.headers))
        print("Response body:", response.text)
        
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    test_initialize() 