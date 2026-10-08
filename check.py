import app

c = app.get_conn()
cur = c.cursor()

print("=== USUARIOS ===")
cur.execute("SELECT id, email, tipo FROM usuarios LIMIT 5")
for r in cur.fetchall():
    print(r)

print()
print("=== TABELAS ===")
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
for r in cur.fetchall():
    print(r[0])

cur.close()
app.close_conn(c)
