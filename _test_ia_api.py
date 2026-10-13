import app
from fastapi.testclient import TestClient

client = TestClient(app.app)

# Login como admin
r = client.post("/login", data={"email": "matechtecnologia01@gmail.com", "senha": "matech123"}, follow_redirects=False)
print("Login:", r.status_code)

# Testa a rota de status
r2 = client.get("/api/ia-aprende/status")
print("Status API:", r2.status_code, r2.text[:200])
