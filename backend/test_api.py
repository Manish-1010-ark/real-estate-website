import requests
import os
from dotenv import load_dotenv
load_dotenv()

BASE_URL = os.getenv("BASE_URL")

def test_registration():
    data = {"name": "John Doe", "email": "john@example.com", "password": "password123", "role": "buyer"}
    res = requests.post(f"{BASE_URL}/register", json=data)
    print("Register:", res.status_code, res.json())
    return res.json().get("access_token") if res.status_code == 201 else None

def test_login():
    data = {"email": "john@example.com", "password": "password123"}
    res = requests.post(f"{BASE_URL}/login", json=data)
    print("Login:", res.status_code, res.json())
    return res.json().get("access_token") if res.status_code == 200 else None

def test_profile(token):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{BASE_URL}/profile", headers=headers)
    print("Profile:", res.status_code, res.json())

def run_all():
    token = test_registration()
    login_token = test_login()
    if login_token:
        test_profile(login_token)
    print("\n✅ All tests completed!")

if __name__ == '__main__':
    run_all()