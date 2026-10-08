import app
c = app.get_conn()
cur = c.cursor()

# Ver se tabela de empresas sob gestão existe
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE '%gest%'")
print("Tabelas gestao:", [r[0] for r in cur.fetchall()])

cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE '%cuid%'")
print("Tabelas cuida:", [r[0] for r in cur.fetchall()])

cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE '%empresa%'")
print("Tabelas empresa:", [r[0] for r in cur.fetchall()])

cur.close()
app.close_conn(c)
