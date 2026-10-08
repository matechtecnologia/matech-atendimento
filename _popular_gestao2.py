import app
c = app.get_conn()
cur = c.cursor()

cur.execute("SELECT COUNT(*) FROM projects WHERE tipo='cliente' OR tipo='consultoria'")
if cur.fetchone()[0] == 0:
    cur.execute("""INSERT INTO projects 
        (nome, descricao, tipo, status, prioridade, percentual)
        VALUES (%s, %s, %s, %s, %s, %s)""",
        ("M.A Tech (interna)", "Empresa dona do sistema - gestao propria", "cliente", "em_andamento", "alta", 30))

    cur.execute("""INSERT INTO projects 
        (nome, descricao, tipo, status, prioridade, percentual)
        VALUES (%s, %s, %s, %s, %s, %s)""",
        ("Cliente Modelo 1", "Empresa piloto para validacao", "cliente", "em_andamento", "alta", 10))
    
    c.commit()
    print("2 empresas inseridas em projects")
else:
    print("ja tem")

cur.close()
app.close_conn(c)
