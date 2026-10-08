import app
c = app.get_conn()
cur = c.cursor()
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='custos_mensais' ORDER BY ordinal_position")
for r in cur.fetchall():
    print(r[0])
cur.close()
app.close_conn(c)
