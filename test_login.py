"""
Test script to verify admin login works correctly
"""
import requests
import json

# Test admin login
url = "http://localhost:8000/api/auth/login"
payload = {
    "email": "admin@fst.utm.tn",
    "mot_de_passe": "Admin@2026"
}

print("Testing admin login...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print()

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("\n✅ Login successful!")
        data = response.json()
        print(f"Token: {data.get('access_token', 'N/A')[:50]}...")
        print(f"User Type: {data.get('user', {}).get('type', 'N/A')}")
        print(f"User Email: {data.get('user', {}).get('email', 'N/A')}")
    else:
        print("\n❌ Login failed!")
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to backend. Make sure it's running on http://localhost:8000")
except Exception as e:
    print(f"❌ Error: {e}")
