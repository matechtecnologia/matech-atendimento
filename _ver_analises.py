import app
c = app.get_conn()
cur = c.cursor()

# Verifica analises salvas
cur.execute("SELECT id, atendimento_id, inventou, campo_faltante, criado_em FROM analises_ia ORDER BY id DESC LIMIT 5")
rows = cur.fetchall()
if rows:
    print("=== ULTIMAS ANALISES ===")
    for r in rows:
        print(f"ID: {r[0]} | Atend: {r[1]} | Inventou: {r[2]} | Campo: {r[3]} | {r[4]}")
else:
    print("Nenhuma analise salva ainda")

# Verifica acumulado
cur.execute("SELECT analises_acumuladas FROM vendedores WHERE usuario_id = 1")
r = cur.fetchone()
print(f"\nAnalises acumuladas: {r[0] if r else 'nao encontrado'}")

cur.close()
app.close_conn(c)
