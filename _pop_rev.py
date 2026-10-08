import app
c = app.get_conn()
cur = c.cursor()

cur.execute("INSERT INTO revenue_records (descricao, valor, tipo, cliente, status) VALUES (%s, %s, %s, %s, %s)", ("Plano Basico - Cliente 1", 97, "software", "Cliente 1", "recebido"))
cur.execute("INSERT INTO revenue_records (descricao, valor, tipo, cliente, status) VALUES (%s, %s, %s, %s, %s)", ("Plano Pro - Cliente 2", 297, "software", "Cliente 2", "recebido"))
cur.execute("INSERT INTO revenue_records (descricao, valor, tipo, cliente, status) VALUES (%s, %s, %s, %s, %s)", ("Consultoria avulsa - Cliente 3", 497, "consultoria", "Cliente 3", "recebido"))
c.commit()

cur.execute("SELECT COUNT(*) FROM revenue_records")
print(f"Total: {cur.fetchone()[0]}")

cur.close()
app.close_conn(c)
