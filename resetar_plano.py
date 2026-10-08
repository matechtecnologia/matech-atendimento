# resetar_plano.py
# APAGA tudo do Plano e popula com o conteudo dos 10 documentos.

import app

c = app.get_conn()
cur = c.cursor()

print("=== LIMPANDO TABELAS DO PLANO ===")

# Ordem importa por causa das FKs
cur.execute("DELETE FROM tasks")
cur.execute("DELETE FROM goals")
cur.execute("DELETE FROM roadmap_phases")
cur.execute("DELETE FROM products")
cur.execute("DELETE FROM projects")
cur.execute("DELETE FROM blockers")
cur.execute("DELETE FROM decisions")
cur.execute("DELETE FROM metrics")

# Resetar sequencias de ID
cur.execute("ALTER SEQUENCE tasks_id_seq RESTART WITH 1")
cur.execute("ALTER SEQUENCE goals_id_seq RESTART WITH 1")
cur.execute("ALTER SEQUENCE roadmap_phases_id_seq RESTART WITH 1")
cur.execute("ALTER SEQUENCE products_id_seq RESTART WITH 1")
cur.execute("ALTER SEQUENCE projects_id_seq RESTART WITH 1")
cur.execute("ALTER SEQUENCE blockers_id_seq RESTART WITH 1")
cur.execute("ALTER SEQUENCE decisions_id_seq RESTART WITH 1")
cur.execute("ALTER SEQUENCE metrics_id_seq RESTART WITH 1")

print("  Limpo.")

print()
print("=== POPULANDO ROADMAP_PHASES (9 fases do Doc 1) ===")
fases = [
    (1, "M.A Tech Atendimento IA", "Primeiro produto: IA que ajuda vendedor a atender e vender", "concluido", 100),
    (2, "M.A Tech Consultoria IA", "Segundo produto: IA que diagnostica o negocio do dono", "concluido", 100),
    (3, "Validacao comercial", "Conseguir os primeiros 5 clientes pagantes", "em_execucao", 5),
    (4, "Primeiros clientes", "Retencao e validacao de preco", "planejado", 0),
    (5, "Modulo Gestao", "Controle financeiro, DRE, fluxo de caixa", "planejado", 0),
    (6, "Modulo CRM", "Kanban de vendas, pipeline, follow-up automatico", "planejado", 0),
    (7, "Modulo Trafego Pago", "Meta Ads + Google Ads + otimizacao por IA", "planejado", 0),
    (8, "Modulo Automacao", "Workflow builder + gatilhos + integracoes", "planejado", 0),
    (9, "Expansao Global", "LATAM (Mercado Pago) + Stripe + multi-regiao", "planejado", 0),
]
for f in fases:
    cur.execute("""INSERT INTO roadmap_phases (numero, nome, descricao, status, percentual)
                   VALUES (%s, %s, %s, %s, %s)""", f)
print(f"  {len(fases)} fases inseridas")

print()
print("=== POPULANDO PRODUCTS (6 modulos do Doc 1) ===")
produtos = [
    ("M.A Tech Atendimento IA", "IA que ajuda vendedor a atender e vender. Devolve 4 blocos: o que falar, texto, estagio, CRM.", "producao", "critica"),
    ("M.A Tech Consultoria IA", "IA que diagnostica o negocio do dono. Detecta gargalo e indica servico.", "producao", "critica"),
    ("M.A Tech Gestao", "Controle financeiro, DRE simplificado, fluxo de caixa, contas a pagar/receber.", "planejado", "alta"),
    ("M.A Tech CRM", "Kanban de vendas, pipeline personalizavel, follow-up automatico, previsao de vendas.", "planejado", "alta"),
    ("M.A Tech Trafego Pago", "Integracao Meta Ads e Google Ads. Dashboard, analise de metricas, sugestao de otimizacao.", "planejado", "media"),
    ("M.A Tech Automacao", "Workflow builder visual. Gatilhos, acoes, integracoes (Zapier, Make), templates.", "planejado", "media"),
]
for p in produtos:
    cur.execute("""INSERT INTO products (nome, descricao, status, prioridade)
                   VALUES (%s, %s, %s, %s)""", p)
print(f"  {len(produtos)} produtos inseridos")

print()
print("=== POPULANDO GOALS (metas do Doc 8 e Doc 10) ===")
# Primeiro pega os IDs das fases
cur.execute("SELECT id, numero FROM roadmap_phases")
fases_id = {row[1]: row[0] for row in cur.fetchall()}
f2 = fases_id.get(2)  # Consultoria IA
f3 = fases_id.get(3)  # Validacao comercial
f4 = fases_id.get(4)  # Primeiros clientes
f9 = fases_id.get(9)  # Expansao Global

metas = [
    ("Conseguir 5 clientes pagantes", "Primeira validacao comercial", "clientes_pagantes", 0, 0, 5, "clientes", "em_andamento", "critica", f3),
    ("Conseguir 10 clientes pagantes", "Consolidar produto no mercado", "clientes_pagantes", 0, 0, 10, "clientes", "nao_iniciado", "alta", f4),
    ("Conseguir 30 clientes pagantes", "Primeira escala", "clientes_pagantes", 0, 0, 30, "clientes", "nao_iniciado", "media", f4),
    ("Conseguir 100 clientes pagantes", "Escala comercial", "clientes_pagantes", 0, 0, 100, "clientes", "nao_iniciado", "baixa", f9),
    ("MRR de R$ 5.000", "Meta financeira curto prazo", "mrr", 0, 0, 5000, "R$", "nao_iniciado", "alta", f3),
    ("MRR de R$ 20.000", "Meta financeira medio prazo", "mrr", 0, 0, 20000, "R$", "nao_iniciado", "media", f4),
    ("MRR de R$ 60.000", "Meta financeira longo prazo", "mrr", 0, 0, 60000, "R$", "nao_iniciado", "baixa", f9),
    ("Publicar landing page", "Site de vendas no ar", "landing", 0, 0, 1, "unidade", "nao_iniciado", "critica", f3),
    ("Migrar Asaas para producao", "Aceitar PIX real", "asaas", 0, 0, 1, "unidade", "nao_iniciado", "critica", f3),
    ("Abrir CNPJ", "Regularizar empresa para pagamento real", "cnpj", 0, 0, 1, "unidade", "nao_iniciado", "critica", f3),
]
for m in metas:
    cur.execute("""INSERT INTO goals (titulo, descricao, indicador, valor_inicial, valor_atual, valor_meta, unidade, status, prioridade, fase_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", m)
print(f"  {len(metas)} metas inseridas")

print()
print("=== POPULANDO TASKS (Doc 2 - Plano de Execucao) ===")
cur.execute("SELECT id FROM goals WHERE titulo LIKE '%5 clientes%' LIMIT 1")
g5 = cur.fetchone()[0]
cur.execute("SELECT id FROM goals WHERE titulo LIKE '%landing page%' LIMIT 1")
g_land = cur.fetchone()[0]
cur.execute("SELECT id FROM goals WHERE titulo LIKE '%Asaas%' LIMIT 1")
g_asaas = cur.fetchone()[0]
cur.execute("SELECT id FROM goals WHERE titulo LIKE '%CNPJ%' LIMIT 1")
g_cnpj = cur.fetchone()[0]

tarefas = [
    # PRIORIDADE ALTA - essa semana
    ("Tela de transicao da Consultoria", "Loading com foto do consultor + frases rotativas", g5, "pendente", "critica"),
    ("Mapa das 17 telas do Plano", "Documentar o que cada tela registra", None, "concluida", "critica"),
    ("Layout dos botoes da Consultoria", "Consultor em cima, botoes lado a lado embaixo", None, "pendente", "alta"),
    ("IA usar gargalo salvo nas proximas mensagens", "Business context na proxima interacao", None, "pendente", "alta"),
    ("WhatsApp obrigatorio no cadastro", "Campo + validacao + unique", None, "pendente", "alta"),
    ("Limite de IP no cadastro", "Max 3 contas por IP por hora", None, "pendente", "alta"),
    ("LGPD + Termos de uso", "Paginas /termos e /privacidade + checkbox", None, "pendente", "alta"),
    ("Migrar Asaas sandbox para producao", "Chave producao + webhook + PIX de teste", g_asaas, "pendente", "critica"),
    ("Trial de 7 dias", "Campo trial_expira_em + logica de expiracao", None, "pendente", "alta"),
    ("Landing page", "Hero, problema, solucao, modulos, precos, CTA", g_land, "pendente", "critica"),
    ("Comprar dominio matech.com.br", "Registro.br + DNS no Render + SSL", None, "pendente", "alta"),
    ("Abrir CNPJ", "Regularizar empresa para Asaas producao", g_cnpj, "pendente", "critica"),
    
    # PRIORIDADE MEDIA - proximas 2 semanas
    ("SEO basico", "Meta tags + sitemap + robots + Search Console", g_land, "pendente", "media"),
    ("Dashboard do vendedor", "Leads, taxa de conversao, estagios, evolucao", None, "pendente", "media"),
    ("Relatorio automatico semanal", "Email toda segunda com resumo da semana", None, "pendente", "media"),
    ("Pos-venda automatico", "Acompanhamento 7, 30, 90 dias", None, "pendente", "media"),
    ("Programa de indicacao", "Link unico + desconto pra quem indica", None, "pendente", "media"),
    ("PWA (app no navegador)", "Manifest + service worker + icone", None, "pendente", "media"),
    ("Notificacoes push", "Cliente respondeu, gargalo detectado, pagamento confirmado", None, "pendente", "media"),
    ("Tutoriais interativos", "Onboarding guiado + videos 30s + tooltips", None, "pendente", "media"),
    
    # PRIORIDADE BAIXA - proximo mes
    ("Google Calendar", "Botao agendar reuniao dentro da Consultoria", None, "pendente", "baixa"),
    ("Envio do diagnostico por email", "Resend ou SendGrid - resumo da consultoria", None, "pendente", "baixa"),
    ("Modulo Gestao completo", "Dashboard financeiro + contas + DRE + KPIs", None, "pendente", "baixa"),
    ("Modulo CRM completo", "Kanban + pipeline + automacao + previsao", None, "pendente", "baixa"),
    ("Modulo Trafego Pago", "Meta Ads + Google Ads + otimizacao por IA", None, "pendente", "baixa"),
    ("Modulo Automacao", "Workflow builder + gatilhos + Zapier/Make", None, "pendente", "baixa"),
    ("WhatsApp Business API", "Envio automatico de texto e audio", None, "pendente", "baixa"),
    ("Stripe global", "Pagamento em USD/EUR + GDPR", None, "pendente", "baixa"),
]
for t in tarefas:
    cur.execute("""INSERT INTO tasks (titulo, descricao, goal_id, status, prioridade)
                   VALUES (%s, %s, %s, %s, %s)""", t)
print(f"  {len(tarefas)} tarefas inseridas")

print()
print("=== POPULANDO PROJECTS (Doc 10 - Lancamento) ===")
projetos = [
    ("Popular Plano M.A Tech", "Conteudo real nas 17 telas", "em_andamento", "critica", 100),
    ("Migrar Asaas para producao", "Sair do sandbox e aceitar PIX real", "pendente", "critica", 0),
    ("Landing page no ar", "Site de vendas em matech.com.br", "pendente", "critica", 0),
    ("Comprar dominio matech.com.br", "Registro.br + DNS + SSL", "pendente", "alta", 0),
    ("Abrir CNPJ", "Regularizar M.A Tech como empresa", "pendente", "critica", 0),
    ("Primeiros 10 clientes testando", "Fase 1 do lancamento (Doc 10)", "pendente", "critica", 0),
    ("Primeiros 5 clientes pagantes", "Fase 2 do lancamento (Doc 10)", "pendente", "critica", 0),
]
for p in projetos:
    cur.execute("""INSERT INTO projects (nome, descricao, status, prioridade, percentual)
                   VALUES (%s, %s, %s, %s, %s)""", p)
print(f"  {len(projetos)} projetos inseridos")

print()
print("=== POPULANDO BLOCKERS (Doc 8 - Riscos) ===")
bloqueios = [
    ("Sem CNPJ", "Nao da pra usar Asaas producao sem CNPJ. Bloqueia pagamento real.", "Alto - bloqueia receita", "Abrir CNPJ ou usar MEI", "critica"),
    ("Groq pode descontinuar free tier", "Toda a IA depende do Groq gratis. Se mudar, quebra.", "Alto - bloqueia produto", "Multi-provedor (OpenAI, Anthropic)", "alta"),
    ("Supabase free tier pode estourar", "500MB + 2GB bandwidth. Com 100+ clientes, estoura.", "Medio - forca upgrade", "Migrar para Supabase Pro (US$25/mes)", "media"),
    ("Sem usuarios ativos suficientes", "Poucos usuarios testando para validar comercialmente.", "Alto - bloqueia validacao", "Conseguir 10+ usuarios testando", "critica"),
    ("Churn alto (risco futuro)", "Se clientes cancelarem, negocio nao escala.", "Alto - bloqueia crescimento", "Focar em resultado real + suporte rapido", "media"),
    ("LGPD sem compliance", "Multa potencial se dados vazarem.", "Medio - risco legal", "Implementar LGPD + termos + privacidade", "alta"),
]
for b in bloqueios:
    cur.execute("""INSERT INTO blockers (titulo, problema, impacto, solucao_necessaria, prioridade)
                   VALUES (%s, %s, %s, %s, %s)""", b)
print(f"  {len(bloqueios)} bloqueios inseridos")

print()
print("=== POPULANDO DECISIONS (arquiteturais) ===")
decisoes = [
    ("2 IAs especializadas", "Atendimento IA + Consultoria IA como diferenciais", "Ninguem tem 2 IAs especializadas", "1 IA generica", "Diferencial competitivo", "tomada"),
    ("3 camadas: M.A Tech -> Vendedor -> Cliente final", "Arquitetura de produto", "Modelo escalavel", "Venda direta", "Growth embutido", "tomada"),
    ("Freemium + assinatura (R$97-597)", "Modelo de negocio", "Captura base grande", "So pago", "MRR previsivel", "tomada"),
    ("PIX como pagamento inicial", "Mercado brasileiro", "PIX e padrao BR", "Cartao + boleto", "Menor friccao", "tomada"),
    ("2 chamadas Groq (resposta + extracao)", "Extracao de gargalo/servico", "Separar responsabilidades", "1 chamada", "Metadados precisos", "tomada"),
    ("Migrar para CNPJ antes de Asaas producao", "Requisito legal", "Nao da pra cobrar sem CNPJ", "MEI", "Pagamento regular", "planejada"),
    ("Landing page antes de marketing pago", "Ordem de lancamento", "Sem landing, sem conversao", "Ads direto", "CAC menor", "planejada"),
]
for d in decisoes:
    cur.execute("""INSERT INTO decisions (titulo, decisao, motivo, alternativas, impacto_esperado, status)
                   VALUES (%s, %s, %s, %s, %s, %s)""", d)
print(f"  {len(decisoes)} decisoes inseridas")

print()
print("=== POPULANDO METRICS (Doc 8) ===")
metricas = [
    ("Usuarios cadastrados", "produto", 7, "unidade"),
    ("Clientes pagantes", "comercial", 0, "unidade"),
    ("MRR", "financeiro", 0, "R$"),
    ("Consultorias realizadas", "produto", 6, "unidade"),
    ("Atendimentos gerados", "produto", 9, "unidade"),
    ("Nichos cadastrados", "produto", 0, "unidade"),
    ("CAC (custo aquisicao)", "comercial", 0, "R$"),
    ("LTV (valor do cliente)", "comercial", 0, "R$"),
    ("Churn mensal", "comercial", 0, "%"),
    ("NPS (satisfacao)", "produto", 0, "pontos"),
]
for m in metricas:
    cur.execute("""INSERT INTO metrics (nome, categoria, valor, unidade)
                   VALUES (%s, %s, %s, %s)""", m)
print(f"  {len(metricas)} metricas inseridas")

c.commit()
cur.close()
app.close_conn(c)

print()
print("========================================")
print("PLANO M.A TECH POPULADO DO ZERO")
print("========================================")
