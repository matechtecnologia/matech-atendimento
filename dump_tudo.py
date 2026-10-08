import app
c = app.get_conn()
cur = c.cursor()

for tabela in ["roadmap_phases", "goals", "tasks", "products", "projects", "blockers", "decisions", "metrics"]:
    cur.execute(f"SELECT * FROM {tabela} ORDER BY id LIMIT 50")
    cols = [d[0] for d in cur.description]
    print(f"=== {tabela} ({cols}) ===")
    for r in cur.fetchall():
        print(" ", r)
    print()

cur.close()
app.close_conn(c)
