import app
c = app.get_conn()
cur = c.cursor()

cur.execute("SELECT COUNT(*) FROM revenue_records")
if cur.fetchone()[0] == 0:
    cur.execute("INSERT INTO revenue_records (tipo, descricao, valor, cliente, status) VALUES (%s, %s, %s, %s, %s)", ("atendimento", "Plano Básico - Cliente 1", 97, "Cliente 1", "recebido"))
    cur.execute("INSERT INTO revenue_records (tipo, descricao, valor, cliente, status) VALUES (%s, %s, %s, %s, %s)", ("atendimento", "Plano Pro - Cliente 2", 297, "Cliente 2", "recebido"))
    cur.execute("INSERT INTO revenue_records (tipo, descricao, valor, cliente, status) VALUES (%s, %s, %s, %s, %s)", ("consultoria", "Sessão avulsa", 497, "Cliente 3", "recebido"))
    print("3 receitas inseridas")

cur.execute("SELECT COUNT(*) FROM custos_mensais")
if cur.fetchone()[0] == 0:
    cur.execute("INSERT INTO custos_mensais (mes, ano, descricao, categoria, valor) VALUES (10, 2026, 'Render', 'infra', 40)")
    cur.execute("INSERT INTO custos_mensais (mes, ano, descricao, categoria, valor) VALUES (10, 2026, 'Supabase', 'infra', 0)")
    cur.execute("INSERT INTO custos_mensais (mes, ano, descricao, categoria, valor) VALUES (10, 2026, 'Groq IA', 'ia', 0)")
    cur.execute("INSERT INTO custos_mensais (mes, ano, descricao, categoria, valor) VALUES (10, 2026, 'Dominio', 'infra', 3.33)")
    print("4 custos inseridos")

c.commit()
print("OK")
cur.close()
app.close_conn(c)
