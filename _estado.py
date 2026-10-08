import app
c = app.get_conn()
cur = c.cursor()

for t in ["roadmap_phases","goals","tasks","products","projects","blockers","decisions","metrics","journal_entries","revenue_records","custos_mensais"]:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"{t}: {cur.fetchone()[0]}")

cur.close()
app.close_conn(c)
