import app
c = app.get_conn()
cur = c.cursor()
cur.execute("SELECT id FROM atendimentos ORDER BY id DESC LIMIT 1")
r = cur.fetchone()
print("Ultimo atendimento:", r[0] if r else "nenhum")
cur.close()
app.close_conn(c)
