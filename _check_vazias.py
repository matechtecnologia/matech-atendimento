import app
c = app.get_conn()
cur = c.cursor()

tabelas = ["leads_landing", "revenue_records", "custos_mensais", "metrics", "products"]
for t in tabelas:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        print(f"{t}: {cur.fetchone()[0]}")
    except Exception as e:
        print(f"{t}: ERRO - {e}")

cur.close()
app.close_conn(c)
