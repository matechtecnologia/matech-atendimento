# popular_plano.py
# Popula as tabelas do Plano M.A Tech com conteudo real.
# Idempotente: se rodar 2x, nao duplica.

import app

c = app.get_conn()
cur = c.cursor()

def inserir_uma(tabela, sql_check, sql_insert, params):
    cur.execute(sql_check, params[:1] if params else ())
    if cur.fetchone()[0] == 0:
        cur.execute(sql_insert, params)

print("Populando Plano...")

# ============================================================
# ROADMAP_PHASES — 9 fases
# ============================================================
cur.execute("SELECT COUNT(*) FROM roadmap_phases")
if cur.fetchone()[0] == 0:
    fases = [
        (1, "M.A Tech Atendimento com IA", "Produto 01 construido e em producao", "concluido", 100),
        (2, "Validacao comercial", "Conseguir os primeiros 5 clientes pagantes", "em_execucao", 10),
        (3, "Primeiros clientes", "Retencao e validacao de preco", "planejado", 0),
        (4, "Produto em producao estavel", "Melhoria continua do Atendimento IA", "planejado", 0),
        (5, "Modulo Gestao", "Inicio do Produto 02 - M.A Tech Gestao", "planejado", 0),
        (6, "Modulo CRM", "Pipeline comercial completo", "planejado", 0),
        (7, "Modulo Trafego Pago", "Integracao Meta Ads + Google Ads", "planejado", 0),
        (8, "Modulo Automacao", "Workflow builder + gatilhos", "planejado", 0),
        (9, "Expansao Global", "LATAM + Stripe + multi-regiao", "planejado", 0),
    ]
    for f in fases:
        cur.execute("""INSERT INTO roadmap_phases (numero, nome, descricao, status, percentual)
                       VALUES (%s, %s, %s, %s, %s)""", f)
    print(f"  roadmap_phases: {len(fases)} fases")
else:
    print("  roadmap_phases: ja tem dados, pulando")

# ============================================================
# PRODUCTS — 6 produtos
# ============================================================
cur.execute("SELECT COUNT(*) FROM products")
if cur.fetchone()[0] == 0:
    produtos = [
        ("M.A Tech Atendimento IA", "IA que ajuda vendedor a atender e vender", "producao", "critica"),
        ("M.A Tech Consultoria IA", "IA que diagnostica o negocio do dono", "producao", "critica"),
        ("M.A Tech Gestao", "Dashboard financeiro, DRE, fluxo de caixa", "planejado", "alta"),
        ("M.A Tech CRM", "Kanban, pipeline, follow-up automatico", "planejado", "alta"),
        ("M.A Tech Trafego Pago", "Gestao de campanhas Meta e Google Ads", "planejado", "media"),
        ("M.A Tech Automacao", "Workflow builder + integracoes", "planejado", "media"),
    ]
    for p in produtos:
        cur.execute("""INSERT INTO products (nome, descricao, status, prioridade)
                       VALUES (%s, %s, %s, %s)""", p)
    print(f"  products: {len(produtos)} produtos")

# ============================================================
# PROJECTS — 4 projetos
# ============================================================
cur.execute("SELECT COUNT(*) FROM projects")
if cur.fetchone()[0] == 0:
    projetos = [
        ("Popular as 17 telas do Plano", "Preencher tabelas do Plano com conteudo real", "em_andamento", "alta", 10),
        ("Migrar Asaas para producao", "Sair do sandbox e aceitar PIX real", "planejado", "critica", 0),
        ("Landing page publicada", "Site de vendas em matech.com.br", "planejado", "critica", 0),
        ("Comprar dominio matech.com.br", "Registro no Registro.br + DNS no Render", "planejado", "alta", 0),
    ]
    for p in projetos:
        cur.execute("""INSERT INTO projects (nome, descricao, status, prioridade, percentual)
                       VALUES (%s, %s, %s, %s, %s)""", p)
    print(f"  projects: {len(projetos)} projetos")

# ============================================================
# GOALS — 8 metas
# ============================================================
cur.execute("SELECT COUNT(*) FROM goals")
if cur.fetchone()[0] == 0:
    metas = [
        ("Conseguir os primeiros 5 clientes pagantes", "Primeira meta comercial", "clientes_pagantes", 0, 0, 5, "clientes", "em_andamento", "critica"),
        ("Conseguir 10 clientes pagantes", "Segunda meta comercial", "clientes_pagantes", 0, 0, 10, "clientes", "nao_iniciado", "alta"),
        ("Conseguir 30 clientes pagantes", "Meta de escala inicial", "clientes_pagantes", 0, 0, 30, "clientes", "nao_iniciado", "media"),
        ("Conseguir 100 clientes pagantes", "Meta de escala", "clientes_pagantes", 0, 0, 100, "clientes", "nao_iniciado", "baixa"),
        ("MRR de R$ 5.000", "Meta financeira curto prazo", "mrr", 0, 0, 5000, "R$", "nao_iniciado", "alta"),
        ("MRR de R$ 20.000", "Meta financeira medio prazo", "mrr", 0, 0, 20000, "R$", "nao_iniciado", "media"),
        ("Landing page publicada", "Site de vendas no ar", "landing", 0, 0, 1, "unidade", "nao_iniciado", "critica"),
        ("Asaas em producao", "Aceitar PIX real", "asaas", 0, 0, 1, "unidade", "nao_iniciado", "critica"),
    ]
    for m in metas:
        cur.execute("""INSERT INTO goals (titulo, descricao, indicador, valor_inicial, valor_atual, valor_meta, unidade, status, prioridade)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", m)
    print(f"  goals: {len(metas)} metas")

# ============================================================
# TASKS — 15 tarefas
# ============================================================
cur.execute("SELECT COUNT(*) FROM tasks")
if cur.fetchone()[0] == 0:
    cur.execute("SELECT id FROM goals WHERE titulo LIKE '%5 clientes%' LIMIT 1")
    r = cur.fetchone(); g5 = r[0] if r else None
    cur.execute("SELECT id FROM goals WHERE titulo LIKE '%Landing%' LIMIT 1")
    r = cur.fetchone(); g_land = r[0] if r else None

    tarefas = [
        ("Popular as 17 telas do Plano", "Preencher tabelas com conteudo real", g5, "em_andamento", "critica"),
        ("Migrar Asaas para producao", "Sair do sandbox", g5, "pendente", "critica"),
        ("Criar landing page", "Site de vendas", g_land, "pendente", "critica"),
        ("Comprar dominio matech.com.br", "Registro.br + DNS", None, "pendente", "alta"),
        ("Resolver bug de login em /plano", "Cookie nao esta sendo enviado", None, "pendente", "alta"),
        ("Criar as 2 telas faltantes (/plano/pendencias e /plano/proximos)", "Fechar as 17 telas", None, "pendente", "alta"),
        ("Limpar duplicacao do plano_install.py", "ROI e comerciais aparecem 2x", None, "pendente", "media"),
        ("Resolver erro cosmetico 'strategic_plans already exists'", "Log do Render", None, "pendente", "media"),
        ("Encontrar 20 empresas para contato", "Prospeccao inicial", g5, "pendente", "critica"),
        ("Fazer 20 contatos comerciais", "Primeiros leads reais", g5, "pendente", "critica"),
        ("Fazer 5 demonstracoes do produto", "Mostrar o sistema", g5, "pendente", "critica"),
        ("Conseguir 10 testes gratuitos", "Usuarios testando", g5, "pendente", "alta"),
        ("Converter primeiro cliente pagante", "Primeira venda real", g5, "pendente", "critica"),
        ("Criar LinkedIn da M.A Tech", "Marketing inicial", None, "pendente", "media"),
        ("Gravar video de demonstracao", "Mostrar o produto", None, "pendente", "media"),
    ]
    for t in tarefas:
        cur.execute("""INSERT INTO tasks (titulo, descricao, goal_id, status, prioridade)
                       VALUES (%s, %s, %s, %s, %s)""", t)
    print(f"  tasks: {len(tarefas)} tarefas")

# ============================================================
# BLOCKERS — 3 bloqueios
# ============================================================
cur.execute("SELECT COUNT(*) FROM blockers")
if cur.fetchone()[0] == 0:
    bloqueios = [
        ("Sem CNPJ", "Nao da pra usar Asaas producao sem CNPJ", "Alto - bloqueia pagamento real", "Abrir CNPJ ou usar MEI", "critica"),
        ("Bug de login em /plano", "Cookie nao esta sendo enviado corretamente", "Medio - bloqueia acesso ao Plano", "Investigar middleware de auth", "alta"),
        ("Plano sem conteudo", "Telas estao vazias", "Medio - nao bloqueia funcionalidade", "Popular via script Python", "alta"),
    ]
    for b in bloqueios:
        cur.execute("""INSERT INTO blockers (titulo, problema, impacto, solucao_necessaria, prioridade)
                       VALUES (%s, %s, %s, %s, %s)""", b)
    print(f"  blockers: {len(bloqueios)} bloqueios")

# ============================================================
# DECISIONS — 3 decisoes
# ============================================================
cur.execute("SELECT COUNT(*) FROM decisions")
if cur.fetchone()[0] == 0:
    decisoes = [
        ("Centralizar gestao do sistema no Chat 7", "Allan decidiu ter 1 so chat gestor", "Ter 3 chats em paralelo", "Aumentar produtividade", "em_teste"),
        ("Popular tabelas do Plano com conteudo dos 10 documentos", "Telas estavam vazias", "Deixar vazio", "Telas com conteudo real", "em_execucao"),
        ("Manter plano_ui.py e aposentar plano_rotas.py", "plano_ui venceu na pratica", "Unificar os dois", "Remover duplicacao", "planejada"),
    ]
    for d in decisoes:
        cur.execute("""INSERT INTO decisions (decisao, motivo, alternativas, impacto_esperado, status)
                       VALUES (%s, %s, %s, %s, %s)""", d)
    print(f"  decisions: {len(decisoes)} decisoes")

# ============================================================
# JOURNAL_ENTRIES — 1 entrada (hoje)
# ============================================================
cur.execute("SELECT COUNT(*) FROM journal_entries WHERE data = CURRENT_DATE")
if cur.fetchone()[0] == 0:
    cur.execute("""INSERT INTO journal_entries (titulo, conteudo, categoria, resultado, proximo_passo)
                   VALUES (%s, %s, %s, %s, %s)""", (
        "Inicio da gestao do sistema pelo Chat 7",
        "Popular as tabelas do Plano com conteudo real. Criar as 2 telas faltantes. "
        "Aposentar plano_rotas.py. Centralizar gestao no Chat 7.",
        "produto",
        "Tabelas populadas",
        "Verificar /plano logado e ajustar conteudo"
    ))
    print("  journal_entries: 1 entrada")

# ============================================================
# METRICS — 6 metricas
# ============================================================
cur.execute("SELECT COUNT(*) FROM metrics")
if cur.fetchone()[0] == 0:
    metricas = [
        ("Usuarios cadastrados", "produto", 5, "unidade"),
        ("Clientes pagantes", "comercial", 0, "unidade"),
        ("MRR", "financeiro", 0, "R$"),
        ("Consultorias realizadas", "produto", 1, "unidade"),
        ("Atendimentos gerados", "produto", 0, "unidade"),
        ("Nichos cadastrados", "produto", 0, "unidade"),
    ]
    for m in metricas:
        cur.execute("""INSERT INTO metrics (nome, categoria, valor, unidade)
                       VALUES (%s, %s, %s, %s)""", m)
    print(f"  metrics: {len(metricas)} metricas")

c.commit()
cur.close()
app.close_conn(c)

print()
print("PRONTO. Tabelas populadas.")
