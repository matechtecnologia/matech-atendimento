import app
from fastapi.testclient import TestClient

# Simula o admin
client = TestClient(app.app)
client.cookies.set("sessao", app.assinar_sessao(1, "admin"))

# Ativa o modo IA que Aprende direto no banco
c = app.get_conn()
cur = c.cursor()
cur.execute("UPDATE vendedores SET ia_aprende_ativo = TRUE WHERE usuario_id = 1")
c.commit()
cur.close()
app.close_conn(c)
print("OK - modo ligado no admin")

# Testa o status
r = client.get("/api/ia-aprende/status")
print(f"Status: {r.status_code} - {r.text}")
