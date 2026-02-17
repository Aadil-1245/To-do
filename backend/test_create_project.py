import requests
from uuid import uuid4

BASE = 'http://127.0.0.1:8000'

def login(email, password):
    r = requests.post(f"{BASE}/auth/login", data={"username": email, "password": password})
    r.raise_for_status()
    return r.json()['access_token']

def create_project(token):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "title": "Auto Project",
        "description": "Created by automated test",
        "start_date": None,
        "end_date": None,
        "technology_stack": "React,FastAPI",
        "team_size": str(uuid4())
    }
    r = requests.post(f"{BASE}/projects", json=payload, headers=headers)
    print(r.status_code, r.text)
    r.raise_for_status()
    return r.json()

if __name__ == '__main__':
    token = login('autotest@example.com', 'password123')
    proj = create_project(token)
    print('Created project', proj)
