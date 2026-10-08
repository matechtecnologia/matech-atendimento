import app
c = app.get_conn()
cur = c.cursor()

# PROJECTS — projetos reais do plano
cur.execute("DELETE FROM projects")
projetos = [
    ("Migrar Asaas para producao", "Sair do sandbox e aceitar PIX real", "produto", "pendente", "critica", 0),
    ("Landing page no ar", "Site de vendas em matech.com.br", "produto", "pendente", "critica", 0),
    ("Comprar dominio matech.com.br", "Registro.br + DNS + SSL", "produto", "pendente", "alta", 0),
    ("Abrir CNPJ", "Regularizar empresa para Asaas producao", "produto", "pendente", "critica", 0),
    ("Conseguir 10 usuarios testando", "Fase 1 do Doc 10", "comercial", "em_andamento", "critica", 10),
    ("Conseguir 5 clientes pagantes", "Fase 2 do Doc 10", "comercial", "pendente", "critica", 0),
]
for p in projetos:
    cur.execute("INSERT INTO projects (nome, descricao, tipo, status, prioridade, percentual) VALUES (%s,%s,%s,%s,%s,%s)", p)

# DECISIONS — decisoes arquiteturais reais
cur.execute("DELETE FROM decisions")
decisoes = [
    ("2 IAs especializadas", "Atendimento IA + Consultoria IA", "Diferencial competitivo", "1 IA generica", "Ninguem mais tem", "tomada"),
    ("3 camadas: M.A Tech > Vendedor > Cliente", "Arquitetura de produto", "Modelo escalavel", "Venda direta", "Growth embutido", "tomada"),
    ("Freemium + assinatura R$97-597", "Modelo de negocio", "Captura base grande", "So pago", "MRR previsivel", "tomada"),
    ("PIX como pagamento", "Mercado brasileiro", "PIX e padrao BR", "Cartao", "Menor friccao", "tomada"),
    ("2 chamadas Groq", "Resposta + extracao de metadados", "Separar responsabilidades", "1 chamada", "Metadados precisos", "tomada"),
    ("Centralizar gestao no Chat 7", "Allan decidiu 1 so chat gestor", "3 chats em paralelo", "Produtividade", "Em teste", "tomada"),
]
for d in decisoes:
    cur.execute("INSERT INTO decisions (titulo, decisao, motivo, alternativas, impacto_esperado, status) VALUES (%s,%s,%s,%s,%s,%s)", d)

# METRICS — metricas reais do Doc 8
cur.execute("DELETE FROM metrics")
metricas = [
    ("Usuarios cadastrados", "produto", 7, "unidade"),
    ("Clientes pagantes", "comercial", 0, "unidade"),
    ("MRR", "financeiro", 0, "R$"),
    ("Consultorias realizadas", "produto", 6, "unidade"),
    ("Atendimentos gerados", "produto", 9, "unidade"),
    ("Nichos cadastrados", "produto", 0, "unidade"),
    ("CAC (custo aquisicao)", "comercial", 0, "R$"),
    ("LTV (valor do cliente)", "comercial", 1500, "R$"),
    ("Churn mensal", "comercial", 0, "%"),
    ("NPS (satisfacao)", "produto", 0, "pontos"),
]
for m in metricas:
    cur.execute("INSERT INTO metrics (nome, categoria, valor, unidade) VALUES (%s,%s,%s,%s)", m)

# CUSTOS_MENSAIS — custos reais
cur.execute("DELETE FROM custos_mensais")
custos = [
    ("Render", "infra", 0, "2026-10"),
    ("Supabase", "infra", 0, "2026-10"),
    ("Groq IA", "ia", 0, "2026-10"),
    ("Dominio matech.com.br", "infra", 3.33, "2026-10"),
    ("Asaas (taxa PIX)", "financeiro", 0, "2026-10"),
]
for cu in custos:
    cur.execute("INSERT INTO custos_mensais (nome, categoria, valor, mes_ano) VALUES (%s,%s,%s,%s)", cu)

c.commit()

for t in ["projects", "decisions", "metrics", "custos_mensais"]:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"{t}: {cur.fetchone()[0]}")

cur.close()
app.close_conn(c)
