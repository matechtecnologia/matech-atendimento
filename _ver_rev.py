import app
c = app.get_conn()
cur = c.cursor()
cur.execute("SELECT id, descricao, valor, tipo, status FROM revenue_records")
for r in cur.fetchall():
    print(r)
cur.close()
app.close_conn(c)
