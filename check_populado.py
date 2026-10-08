import app
c = app.get_conn()
cur = c.cursor()

for tabela in ["roadmap_phases", "products", "projects", "goals", "tasks", "blockers", "decisions", "journal_entries", "metrics"]:
    cur.execute(f"SELECT COUNT(*) FROM {tabela}")
    print(f"{tabela}: {cur.fetchone()[0]}")

cur.close()
app.close_conn(c)
