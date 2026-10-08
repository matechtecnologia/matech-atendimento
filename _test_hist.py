import app
from consultor_db import _get_mensagens
from consultor_core import montar_dossie, formatar_dossie_para_prompt
from consultor import formatar_historico

# Pega a consultoria 19 (a mais recente)
c = app.get_conn()
cur = c.cursor()
cur.execute("SELECT id FROM consultorias WHERE vendedor_id = 3 AND status = 'ativa' ORDER BY id DESC LIMIT 1")
cid = cur.fetchone()[0]
cur.close()
app.close_conn(c)

print(f"Consultoria ativa: #{cid}")
print()

msgs = _get_mensagens(cid, app.get_conn, app.close_conn)
print(f"Total de mensagens: {len(msgs)}")
print()

# Monta o historico como a IA recebe
historico = formatar_historico(msgs[-20:])
print("=== HISTORICO ENVIADO PARA A IA ===")
print(historico)
print("=== FIM ===")
