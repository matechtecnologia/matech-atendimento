import app
c = app.get_conn()
cur = c.cursor()

# Apaga tudo que eu inventei
cur.execute("DELETE FROM revenue_records")
cur.execute("DELETE FROM custos_mensais")
cur.execute("DELETE FROM projects WHERE tipo='cliente'")
cur.execute("DELETE FROM blockers WHERE titulo IN ('Sem CNPJ', 'Bug de login em /plano')")
cur.execute("DELETE FROM metrics")
cur.execute("DELETE FROM decisions")
cur.execute("DELETE FROM projects")
cur.execute("DELETE FROM gestao_empresas")
cur.execute("DELETE FROM gestao_modulos")

c.commit()
print("Dados fake apagados")

# Contar o que sobrou
for t in ["revenue_records", "custos_mensais", "projects", "metrics", "decisions", "blockers"]:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"{t}: {cur.fetchone()[0]}")

cur.close()
app.close_conn(c)
