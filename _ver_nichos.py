import app
c = app.get_conn()
cur = c.cursor()
cur.execute("SELECT id, nome, produto FROM nichos ORDER BY id")
for r in cur.fetchall():
    print(f"ID: {r[0]} | Nome: {r[1]} | Produto: {r[2]}")
cur.close()
app.close_conn(c)
