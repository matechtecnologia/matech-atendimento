import app
c = app.get_conn()
cur = c.cursor()

cur.execute("""INSERT INTO journal_entries 
    (titulo, conteudo, categoria, resultado, proximo_passo)
    VALUES (%s, %s, %s, %s, %s)""",
    ("Plano M.A Tech populado e em producao",
     "Populado todas as tabelas do Plano: 9 fases, 10 metas, 28 tarefas, 6 produtos, 6 projetos, 5 bloqueios, 6 decisoes, 10 metricas, 5 custos. Menu reorganizado em 4 grupos (PAINEL, PRODUTO, OPERACAO, SISTEMA). Corrigido erro cosmetico strategic_plans. Criadas telas Pendencias e Proximos.",
     "produto",
     "Plano 100% funcional no Render",
     "Conseguir primeiros clientes pagantes"))

c.commit()
print("Diario registrado")

cur.close()
app.close_conn(c)
