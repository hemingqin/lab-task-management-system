import requests
import json
import time
from datetime import datetime

BASE_URL = 'http://localhost:5000/api'

def test_debug_users():
    """Test the debug users endpoint"""
    print("\nTesting Debug Users:")
    try:
        response = requests.get(f'{BASE_URL}/auth/debug-users')
        print(f"Response Status Code: {response.status_code}")
        if response.status_code == 404:
            print("Error: Server endpoint not found. Make sure the backend server is running.")
            return False
        if response.status_code == 200:
            try:
                print(f"Response Body: {json.dumps(response.json(), indent=2)}")
                return True
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON response. Raw response: {response.text}")
                return False
        else:
            print(f"Error: Unexpected status code. Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the backend server is running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_register():
    """Test user registration"""
    print("\nTesting Registration:")
    try:
        # Generate a unique email using timestamp
        timestamp = int(time.time())
        data = {
            'username': f'testuser{timestamp}',
            'email': f'test{timestamp}@example.com',
            'password': 'testpass123',
            'role': 'team_member'
        }
        response = requests.post(f'{BASE_URL}/auth/register', json=data)
        print(f"Response Status Code: {response.status_code}")
        if response.status_code == 201:
            try:
                print(f"Response Body: {json.dumps(response.json(), indent=2)}")
                return response.json().get('access_token')
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON response. Raw response: {response.text}")
                return None
        else:
            print(f"Error: Registration failed. Response: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the backend server is running on http://localhost:5000")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_login():
    """Test user login"""
    print("\nTesting Login:")
    try:
        # Generate a unique email using timestamp
        timestamp = int(time.time())
        data = {
            'email': f'test{timestamp}@example.com',
            'password': 'testpass123'
        }
        response = requests.post(f'{BASE_URL}/auth/login', json=data)
        print(f"Response Status Code: {response.status_code}")
        if response.status_code == 200:
            try:
                print(f"Response Body: {json.dumps(response.json(), indent=2)}")
                return response.json().get('access_token')
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON response. Raw response: {response.text}")
                return None
        else:
            print(f"Error: Login failed. Response: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the backend server is running on http://localhost:5000")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_me(token):
    """Test getting current user"""
    print("\nTesting Get Current User:")
    try:
        headers = {
            'Authorization': f'Bearer {token}'
        }
        print(f"Request Headers: {headers}")  # Debug print
        response = requests.get(f'{BASE_URL}/auth/me', headers=headers)
        print(f"Response Status Code: {response.status_code}")
        if response.status_code == 200:
            try:
                print(f"Response Body: {json.dumps(response.json(), indent=2)}")
                return True
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON response. Raw response: {response.text}")
                return False
        else:
            print(f"Error: Get current user failed. Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the backend server is running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    print("Starting API Tests...")
    print("Make sure the backend server is running on http://localhost:5000")
    
    # Test debug users
    if not test_debug_users():
        print("\nDebug users test failed. Please check if the server is running and the endpoint is correct.")
        return
    
    # Test registration and get token
    register_token = test_register()
    if register_token:
        print("\nTesting with registration token...")
        test_me(register_token)
    else:
        print("\nRegistration failed. Skipping registration token test.")
    
    # Test login and get token
    login_token = test_login()
    if login_token:
        print("\nTesting with login token...")
        test_me(login_token)
    else:
        print("\nLogin failed. Skipping login token test.")

if __name__ == '__main__':
    main() 