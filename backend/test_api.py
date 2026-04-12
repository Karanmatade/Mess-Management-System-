import urllib.request
import json

base = "http://localhost:5000/api"
data = json.dumps({"username": "admin", "password": "admin@123"}).encode('utf-8')
req = urllib.request.Request(f"{base}/auth/login", data=data, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as res:
    auth_resp = json.loads(res.read().decode('utf-8'))

token = auth_resp.get("token")
headers = {"Authorization": f"Bearer {token}"}

try:
    req2 = urllib.request.Request(f"{base}/dashboard/", headers=headers)
    with urllib.request.urlopen(req2) as res2:
        d = json.loads(res2.read().decode('utf-8'))
        print("DASHBOARD JSON:")
        print(json.dumps(d, indent=2))
except Exception as e:
    print("Dashboard error:", e)

try:
    req3 = urllib.request.Request(f"{base}/menu/today", headers=headers)
    with urllib.request.urlopen(req3) as res3:
        m = json.loads(res3.read().decode('utf-8'))
        print("MENU JSON:")
        print(json.dumps(m, indent=2))
except Exception as e:
    print("Menu error:", e)
