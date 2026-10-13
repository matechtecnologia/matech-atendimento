import app
c = app.get_conn()
cur = c.cursor()

# Verifica se o modo ja esta ligado
cur.execute("SELECT ia_aprende_ativo FROM vendedores WHERE usuario_id = 1")
r = cur.fetchone()
print(f"ia_aprende_ativo do admin: {r[0] if r else 'nao encontrado'}")

# Verifica as ultimas analises
cur.execute("SELECT COUNT(*) FROM analises_ia")
print(f"Total de analises no banco: {cur.fetchone()[0]}")

cur.close()
app.close_conn(c)
