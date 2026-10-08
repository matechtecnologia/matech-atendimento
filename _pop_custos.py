import app
c = app.get_conn()
cur = c.cursor()

cur.execute("SELECT COUNT(*) FROM custos_mensais")
if cur.fetchone()[0] == 0:
    cur.execute("INSERT INTO custos_mensais (nome, categoria, valor, mes_ano) VALUES (%s, %s, %s, %s)", ("Render", "infra", 40, "2026-10"))
    cur.execute("INSERT INTO custos_mensais (nome, categoria, valor, mes_ano) VALUES (%s, %s, %s, %s)", ("Supabase", "infra", 0, "2026-10"))
    cur.execute("INSERT INTO custos_mensais (nome, categoria, valor, mes_ano) VALUES (%s, %s, %s, %s)", ("Groq IA", "ia", 0, "2026-10"))
    cur.execute("INSERT INTO custos_mensais (nome, categoria, valor, mes_ano) VALUES (%s, %s, %s, %s)", ("Dominio", "infra", 3.33, "2026-10"))
    c.commit()
    print("4 custos inseridos")
else:
    print("ja tem")

cur.close()
app.close_conn(c)
