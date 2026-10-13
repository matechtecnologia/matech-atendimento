import app
from fastapi.testclient import TestClient

client = TestClient(app.app)
client.cookies.set("sessao", app.assinar_sessao(1, "admin"))

# 1. Verifica se o modo esta ligado
c = app.get_conn()
cur = c.cursor()
cur.execute("SELECT id, usuario_id, ia_aprende_ativo FROM vendedores WHERE usuario_id = 1")
r = cur.fetchone()
print(f"Vendedor: {r}")
cur.close()
app.close_conn(c)

# 2. Chama o _rodar_auditoria direto com dados fake
import app as app_module
from datetime import datetime

# Pega um atendimento real
c = app.get_conn()
cur = c.cursor()
cur.execute("SELECT id, o_que_falar FROM atendimentos WHERE status='pronto' ORDER BY id DESC LIMIT 1")
a = cur.fetchone()
cur.close()
app.close_conn(c)

print(f"Atendimento teste: {a}")

if a:
    r_fake = {"o_que_falar": a[1] or "teste", "texto_para_enviar": "", "estagio": "Em Atendimento", "linha_crm": ""}
    nicho_fake = {"id": 14, "produto": "Sistema de atendimento IA"}
    
    print("Rodando auditoria...")
    app_module._rodar_auditoria(a[0], 1, r_fake, nicho_fake)
    print("OK - auditoria executada")
