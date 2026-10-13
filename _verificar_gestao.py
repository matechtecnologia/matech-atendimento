import app
c = app.get_conn()
cur = c.cursor()
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema='public' 
      AND (table_name LIKE '%gestao%' 
        OR table_name LIKE '%financ%' 
        OR table_name LIKE '%receita%' 
        OR table_name LIKE '%custo%' 
        OR table_name LIKE '%lancamento%')
    ORDER BY table_name
""")
tabelas = [r[0] for r in cur.fetchall()]
if tabelas:
    print("TABELAS ENCONTRADAS:")
    for t in tabelas:
        print(f"  - {t}")
else:
    print("NENHUMA TABELA de gestao/financeiro")
cur.close()
app.close_conn(c)
