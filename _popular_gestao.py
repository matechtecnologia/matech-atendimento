import app
c = app.get_conn()
cur = c.cursor()

cur.execute("SELECT COUNT(*) FROM gestao_empresas")
if cur.fetchone()[0] == 0:
    cur.execute("""INSERT INTO gestao_empresas 
        (nome, responsavel, segmento, status, modulos_ativos, receita_mensal)
        VALUES (%s, %s, %s, %s, %s, %s)""",
        ("M.A Tech (interna)", "Allan", "Tecnologia", "ativa", "Atendimento IA, Consultoria IA", 0))

    cur.execute("""INSERT INTO gestao_empresas 
        (nome, responsavel, segmento, status, modulos_ativos, receita_mensal)
        VALUES (%s, %s, %s, %s, %s, %s)""",
        ("Empresa Modelo 1", "A definir", "Comercio", "prospect", "A definir", 0))

    c.commit()
    print("2 empresas inseridas")
else:
    print("ja tem dados")

cur.close()
app.close_conn(c)
