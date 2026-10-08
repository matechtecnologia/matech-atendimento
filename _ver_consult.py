import app
c = app.get_conn()
cur = c.cursor()

cur.execute("SELECT id, status, gargalo_detectado, servico_indicado FROM consultorias WHERE vendedor_id = 3 ORDER BY id DESC LIMIT 3")
for r in cur.fetchall():
    print(r)

cur.close()
app.close_conn(c)
