import requests
import time
import json
from uuid import uuid4

BASE = 'http://127.0.0.1:8000'

def pretty(obj):
    try:
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except Exception:
        return str(obj)

def main():
    ts = int(time.time())
    email = f"apitest+{ts}@example.com"
    password = "password123"

    print('1) Registering user:', email)
    r = requests.post(f"{BASE}/auth/register", json={
        'name': 'API Test',
        'email': email,
        'password': password
    })
    print('Register ->', r.status_code)
    try:
        print(pretty(r.json()))
    except Exception:
        print(r.text)

    print('\n2) Logging in (form-urlencoded)')
    r2 = requests.post(f"{BASE}/auth/login", data={
        'username': email,
        'password': password
    })
    print('Login ->', r2.status_code)
    try:
        print(pretty(r2.json()))
    except Exception:
        print(r2.text)

    if r2.status_code != 200:
        print('\nLogin failed; aborting create-project test.')
        return

    token = r2.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}

    print('\n3) Creating a project using the token')
    payload = {
        'title': 'API-created Project',
        'description': 'Created by automated sequence',
        'start_date': None,
        'end_date': None,
        'technology_stack': 'React,FastAPI',
        'team_size': str(uuid4())
    }
    r3 = requests.post(f"{BASE}/projects", json=payload, headers=headers)
    print('Create project ->', r3.status_code)
    try:
        print(pretty(r3.json()))
    except Exception:
        print(r3.text)

if __name__ == '__main__':
    main()
