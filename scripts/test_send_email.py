import requests

BASE = 'http://127.0.0.1:5000'
ADMIN_EMAIL = 'admin@csesa.in'
ADMIN_PWD = 'admin123'

# login
r = requests.post(f'{BASE}/admin/login', json={'email': ADMIN_EMAIL, 'password': ADMIN_PWD})
print('login status', r.status_code, r.text)
if r.status_code != 200:
    raise SystemExit('login failed')

token = r.json().get('access_token')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

payload = {
    'mailTo': 'test@example.com',
    'subject': 'CSESA Update',
    'body': 'Welcome to CSESA!',
    'attachment': None
}

r2 = requests.post(f'{BASE}/admin/email/send', headers=headers, json=payload)
print('send status', r2.status_code)
print(r2.text)
