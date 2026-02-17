import requests

def test_register():
    url = "http://127.0.0.1:8000/auth/register"
    payload = {"name": "Auto Test", "email": "autotest@example.com", "password": "password123"}
    r = requests.post(url, json=payload, timeout=5)
    print(r.status_code)
    print(r.text)

if __name__ == '__main__':
    test_register()
