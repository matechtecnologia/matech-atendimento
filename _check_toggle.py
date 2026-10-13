import app
c = app.get_conn()
cur = c.cursor()
cur.execute("SELECT ia_aprende_ativo, analises_acumuladas FROM vendedores WHERE usuario_id = 1")
r = cur.fetchone()
print(f"ia_aprende_ativo: {r[0]}")
print(f"analises_acumuladas: {r[1]}")
cur.close()
app.close_conn(c)
