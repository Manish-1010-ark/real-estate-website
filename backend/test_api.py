import requests
import json
import time

BASE_URL = "http://localhost:5000"

def print_response(title, response):
    print(f"\n{'='*50}")
    print(f"TEST: {title}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    print(f"URL: {response.url}")
    
    try:
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
        return response_data
    except Exception:
        print(f"Raw Response: {response.text}")
        return None

def test_health_check():
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        return print_response("Health Check", response)
    except Exception as e:
        print(f"Health check failed: {e}")
        return None

def test_registration():
    url = f"{BASE_URL}/api/auth/register"
    test_cases = [
        {
            "name": "Valid Customer Registration",
            "data": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "password": "password123",
                "role": "customer",
                "phone": "+1234567890",
                "address": "123 Main St, City, State"
            }
        },
        {
            "name": "Valid Agent Registration",
            "data": {
                "name": "Jane Smith",
                "email": "jane.smith@realestate.com",
                "password": "agentpass456",
                "role": "agent",
                "phone": "+1987654321"
            }
        },
        {
            "name": "Invalid Email Format",
            "data": {
                "name": "Invalid User",
                "email": "invalid-email",
                "password": "password123",
                "role": "customer"
            }
        },
        {
            "name": "Weak Password",
            "data": {
                "name": "Weak Pass User",
                "email": "weak@example.com",
                "password": "123",
                "role": "customer"
            }
        }
    ]
    
    results = []
    for test_case in test_cases:
        try:
            response = requests.post(url, json=test_case["data"])
            result = print_response(f"Register - {test_case['name']}", response)
            results.append((test_case["name"], response.status_code, result))
        except Exception as e:
            print(f"Registration test failed: {e}")
            results.append((test_case["name"], 0, None))
    
    return results

def test_login():
    url = f"{BASE_URL}/api/auth/login"
    test_cases = [
        {
            "name": "Valid Login",
            "data": {
                "email": "john.doe@example.com",
                "password": "password123"
            }
        },
        {
            "name": "Invalid Password",
            "data": {
                "email": "john.doe@example.com",
                "password": "wrongpassword"
            }
        },
        {
            "name": "Non-existent User",
            "data": {
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        }
    ]
    
    access_token = None
    refresh_token = None
    
    for test_case in test_cases:
        try:
            response = requests.post(url, json=test_case["data"])
            result = print_response(f"Login - {test_case['name']}", response)
            if response.status_code == 200 and result:
                access_token = result.get('data', {}).get('access_token')
                refresh_token = result.get('data', {}).get('refresh_token')
        except Exception as e:
            print(f"Login test failed: {e}")
    
    return access_token, refresh_token

def test_protected_routes(access_token):
    if not access_token:
        print("\nSkipping protected route tests - no access token")
        return
    
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(f"{BASE_URL}/api/auth/profile", headers=headers)
        print_response("Get Profile", response)
    except Exception as e:
        print(f"Get profile test failed: {e}")
    
    try:
        update_data = {
            "name": "John Doe Updated",
            "phone": "+1111111111",
            "address": "456 Updated St, New City, State"
        }
        response = requests.put(f"{BASE_URL}/api/auth/profile", headers=headers, json=update_data)
        print_response("Update Profile", response)
    except Exception as e:
        print(f"Update profile test failed: {e}")
    
    try:
        password_data = {
            "current_password": "password123",
            "new_password": "newpassword456"
        }
        response = requests.post(f"{BASE_URL}/api/auth/change-password", headers=headers, json=password_data)
        print_response("Change Password", response)
    except Exception as e:
        print(f"Change password test failed: {e}")

def test_token_refresh(refresh_token):
    if not refresh_token:
        print("\nSkipping token refresh test - no refresh token")
        return None
    
    headers = {"Authorization": f"Bearer {refresh_token}"}
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/refresh", headers=headers)
        result = print_response("Token Refresh", response)
        if response.status_code == 200 and result:
            return result.get('data', {}).get('access_token')
    except Exception as e:
        print(f"Token refresh test failed: {e}")
    
    return None

def test_admin_routes():
    url = f"{BASE_URL}/api/auth/login"
    admin_data = {
        "email": "admin@realestate.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(url, json=admin_data)
        result = print_response("Admin Login", response)
        
        if response.status_code == 200 and result:
            admin_token = result.get('data', {}).get('access_token')
            if admin_token:
                headers = {"Authorization": f"Bearer {admin_token}"}
                response = requests.get(f"{BASE_URL}/api/auth/users", headers=headers)
                print_response("Get All Users (Admin)", response)
    
    except Exception as e:
        print(f"Admin routes test failed: {e}")

def test_unauthorized_access():
    print("\nTesting unauthorized access...")

    try:
        response = requests.get(f"{BASE_URL}/api/auth/profile")
        print_response("Profile Without Token", response)
    except Exception as e:
        print(f"Unauthorized profile test failed: {e}")
    
    try:
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(f"{BASE_URL}/api/auth/users", headers=headers)
        print_response("Admin Route With Invalid Token", response)
    except Exception as e:
        print(f"Invalid token test failed: {e}")

def run_comprehensive_tests():
    print("="*60)
    print("STARTING COMPREHENSIVE API TESTS")
    print("="*60)
    
    test_health_check()
    test_registration()
    time.sleep(1)
    access_token, refresh_token = test_login()
    test_protected_routes(access_token)
    new_access_token = test_token_refresh(refresh_token)
    test_admin_routes()
    test_unauthorized_access()
    
    print("\n" + "="*60)
    print("API TESTS COMPLETED")
    print("="*60)

if __name__ == "__main__":
    try:
        run_comprehensive_tests()
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
    except Exception as e:
        print(f"\nTest suite failed: {e}")
