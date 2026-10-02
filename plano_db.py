# plano_db.py
# M.A Tech — Banco do Painel Estrategico
# Cria todas as tabelas do painel do zero.
# Chamado por plano_install.py

def inicializar_plano(get_conn, close_conn):
    """Cria TODAS as tabelas do painel. Apaga as antigas se existirem."""

    conn = get_conn()
    cur = conn.cursor()

    # ============================================================
    # LIMPEZA (apaga versao antiga se existir)
    # ============================================================
    for t in ["tasks", "goals", "roadmap_phases", "strategic_plans",
              "products", "projects", "metrics", "decisions", "blockers",
              "journal_entries", "weekly_reports", "monthly_reports",
              "revenue_records", "plan_modules"]:
        try:
            cur.execute(f"DROP TABLE IF EXISTS {t} CASCADE")
        except Exception:
            pass

    # ============================================================
    # 1. PLANO ESTRATEGICO (missao, visao, fase atual)
    # ============================================================
    cur.execute("""CREATE TABLE strategic_plans (
        id SERIAL PRIMARY KEY,
        versao INTEGER NOT NULL DEFAULT 1,
        missao TEXT,
        visao TEXT,
        fase_atual TEXT,
        status TEXT DEFAULT 'em_execucao',
        data_inicio DATE DEFAULT CURRENT_DATE,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    # ============================================================
    # 2. ROADMAP — as 9 fases
    # ============================================================
    cur.execute("""CREATE TABLE roadmap_phases (
        id SERIAL PRIMARY KEY,
        numero INTEGER NOT NULL UNIQUE,
        nome TEXT NOT NULL,
        descricao TEXT,
        objetivo TEXT,
        status TEXT DEFAULT 'planejado',
        percentual INTEGER DEFAULT 0,
        dependencias TEXT,
        data_prevista DATE,
        data_real DATE,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    # ============================================================
    # 3. METAS
    # ============================================================
    cur.execute("""CREATE TABLE goals (
        id SERIAL PRIMARY KEY,
        titulo TEXT NOT NULL,
        descricao TEXT,
        indicador TEXT,
        valor_inicial NUMERIC DEFAULT 0,
        valor_atual NUMERIC DEFAULT 0,
        valor_meta NUMERIC NOT NULL,
        unidade TEXT,
        prazo DATE,
        status TEXT DEFAULT 'nao_iniciado',
        prioridade TEXT DEFAULT 'media',
        fase_id INTEGER REFERENCES roadmap_phases(id) ON DELETE SET NULL,
        observacao TEXT,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    # ============================================================
    # 4. TAREFAS
    # ============================================================
    cur.execute("""CREATE TABLE tasks (
        id SERIAL PRIMARY KEY,
        titulo TEXT NOT NULL,
        descricao TEXT,
        goal_id INTEGER REFERENCES goals(id) ON DELETE CASCADE,
        fase_id INTEGER REFERENCES roadmap_phases(id) ON DELETE SET NULL,
        projeto_id INTEGER,
        status TEXT DEFAULT 'pendente',
        prioridade TEXT DEFAULT 'media',
        impacto TEXT,
        esforco TEXT,
        responsavel TEXT,
        prazo DATE,
        concluida_em TIMESTAMP WITH TIME ZONE,
        observacao TEXT,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    # ============================================================
    # 5. PROJETOS
    # ============================================================
    cur.execute("""CREATE TABLE projects (
        id SERIAL PRIMARY KEY,
        nome TEXT NOT NULL,
        descricao TEXT,
        tipo TEXT,
        status TEXT DEFAULT 'planejado',
        prioridade TEXT DEFAULT 'media',
        percentual INTEGER DEFAULT 0,
        responsavel TEXT,
        data_inicio DATE,
        data_prevista DATE,
        data_real DATE,
        observacao TEXT,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    # ============================================================
    # 6. PRODUTOS
    # ============================================================
    cur.execute("""CREATE TABLE products (
        id SERIAL PRIMARY KEY,
        nome TEXT NOT NULL,
        descricao TEXT,
        status TEXT DEFAULT 'planejado',
        prioridade TEXT DEFAULT 'media',
        problema_que_resolve TEXT,
        publico TEXT,
        solucao TEXT,
        modelo_negocio TEXT,
        custo_estimado NUMERIC,
        complexidade TEXT,
        potencial_receita NUMERIC,
        dependencias TEXT,
        fase_id INTEGER REFERENCES roadmap_phases(id) ON DELETE SET NULL,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    # ============================================================
    # 7. METRICAS (snapshot diario)
    # ============================================================
    cur.execute("""CREATE TABLE metrics (
        id SERIAL PRIMARY KEY,
        nome TEXT NOT NULL,
        categoria TEXT,
        valor NUMERIC DEFAULT 0,
        unidade TEXT,
        meta NUMERIC,
        data_referencia DATE DEFAULT CURRENT_DATE,
        observacao TEXT,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    # ============================================================
    # 8. DECISOES
    # ============================================================
    cur.execute("""CREATE TABLE decisions (
        id SERIAL PRIMARY KEY,
        data_decisao DATE DEFAULT CURRENT_DATE,
        titulo TEXT NOT NULL,
        decisao TEXT NOT NULL,
        motivo TEXT,
        alternativas TEXT,
        impacto_esperado TEXT,
        resultado_real TEXT,
        status TEXT DEFAULT 'tomada',
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    # ============================================================
    # 9. BLOQUEIOS
    # ============================================================
    cur.execute("""CREATE TABLE blockers (
        id SERIAL PRIMARY KEY,
        titulo TEXT NOT NULL,
        problema TEXT,
        impacto TEXT,
        responsavel TEXT,
        solucao_necessaria TEXT,
        prazo DATE,
        status TEXT DEFAULT 'aberto',
        prioridade TEXT DEFAULT 'alta',
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        resolvido_em TIMESTAMP WITH TIME ZONE
    )""")

    # ============================================================
    # 10. DIARIO
    # ============================================================
    cur.execute("""CREATE TABLE journal_entries (
        id SERIAL PRIMARY KEY,
        data DATE DEFAULT CURRENT_DATE,
        titulo TEXT NOT NULL,
        conteudo TEXT,
        categoria TEXT,
        resultado TEXT,
        proximo_passo TEXT,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    # ============================================================
    # 11/12. RELATORIOS
    # ============================================================
    cur.execute("""CREATE TABLE weekly_reports (
        id SERIAL PRIMARY KEY,
        semana_inicio DATE NOT NULL,
        semana_fim DATE NOT NULL,
        concluido TEXT,
        em_andamento TEXT,
        atrasado TEXT,
        resultados TEXT,
        problemas TEXT,
        proximas_acoes TEXT,
        principal_gargalo TEXT,
        receita_gerada NUMERIC DEFAULT 0,
        clientes_conquistados INTEGER DEFAULT 0,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""CREATE TABLE monthly_reports (
        id SERIAL PRIMARY KEY,
        mes INTEGER NOT NULL,
        ano INTEGER NOT NULL,
        receita NUMERIC DEFAULT 0,
        custos NUMERIC DEFAULT 0,
        lucro NUMERIC DEFAULT 0,
        mrr NUMERIC DEFAULT 0,
        clientes_total INTEGER DEFAULT 0,
        novos_clientes INTEGER DEFAULT 0,
        cancelamentos INTEGER DEFAULT 0,
        execucao_percentual INTEGER DEFAULT 0,
        principais_resultados TEXT,
        principais_problemas TEXT,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(mes, ano)
    )""")

    # ============================================================
    # 13. RECEITAS
    # ============================================================
    cur.execute("""CREATE TABLE revenue_records (
        id SERIAL PRIMARY KEY,
        data DATE DEFAULT CURRENT_DATE,
        tipo TEXT,
        descricao TEXT,
        valor NUMERIC NOT NULL,
        cliente TEXT,
        status TEXT DEFAULT 'recebido',
        observacao TEXT,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    # ============================================================
    # 14. MODULOS DE PROJETO
    # ============================================================
    cur.execute("""CREATE TABLE plan_modules (
        id SERIAL PRIMARY KEY,
        projeto_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
        modulo TEXT NOT NULL,
        ativo BOOLEAN DEFAULT TRUE,
        observacao TEXT,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    # ============================================================
    # SEEDS — dados iniciais
    # ============================================================

    # Plano
    cur.execute("""INSERT INTO strategic_plans
        (versao, missao, visao, fase_atual, status) VALUES
        (1,
         'A M.A Tech e uma empresa de tecnologia, gestao, atendimento, vendas e solucoes empresariais com IA.',
         'Evoluir de uma empresa que vende ferramentas para uma empresa que estrutura, automatiza e gerencia processos empresariais atraves de tecnologia e IA.',
         'Validacao comercial do M.A Tech Atendimento com IA',
         'em_execucao')""")

    # Roadmap — 9 fases
    fases = [
        (1, "M.A Tech Atendimento com IA", "Produto 01 construido e em producao", "concluido", 100),
        (2, "Validacao comercial", "Conseguir os primeiros 5 clientes pagantes", "em_execucao", 10),
        (3, "Primeiros clientes", "Retencao e validacao de preco", "planejado", 0),
        (4, "Produto em producao", "Melhoria continua do Atendimento", "planejado", 0),
        (5, "Plataforma de Gestao", "Inicio do Produto 02 - M.A Tech Gestao", "planejado", 0),
        (6, "Gestao completa/especifica", "Modulos configuraveis por cliente", "planejado", 0),
        (7, "Integracao Atendimento + Gestao", "Unificar os dois produtos", "planejado", 0),
        (8, "Escala comercial", "Aquisicao em volume", "planejado", 0),
        (9, "Ecossistema M.A Tech", "Ecossistema completo de solucoes", "planejado", 0),
    ]
    for f in fases:
        cur.execute("""INSERT INTO roadmap_phases
            (numero, nome, descricao, status, percentual)
            VALUES (%s, %s, %s, %s, %s)""", f)

    # Produtos
    cur.execute("""INSERT INTO products
        (nome, descricao, status, prioridade)
        VALUES (%s, %s, 'producao', 'critica')""", (
        "M.A Tech Atendimento com IA",
        "Sistema de atendimento comercial com IA: recebe informacoes do negocio, cria IA personalizada, mantem historico, analisa conversas, sugere o que falar, indica proximo passo."
    ))
    cur.execute("""INSERT INTO products
        (nome, descricao, status, prioridade)
        VALUES (%s, %s, 'planejado', 'alta')""", (
        "M.A Tech Gestao",
        "Plataforma para gestao empresarial. Modulos configuraveis: comercial, clientes, leads, financeiro, operacional, estoque, pessoas, tarefas, processos, atendimento, indicadores, relatorios."
    ))

    # Metas (5 metas de clientes)
    cur.execute("SELECT id FROM roadmap_phases WHERE numero=2")
    fase2 = cur.fetchone()[0]
    cur.execute("SELECT id FROM roadmap_phases WHERE numero=3")
    fase3 = cur.fetchone()[0]
    cur.execute("SELECT id FROM roadmap_phases WHERE numero=8")
    fase8 = cur.fetchone()[0]

    metas = [
        ("Conseguir os primeiros 5 clientes pagantes", "Primeira meta comercial", "clientes_pagantes", 0, 5, "clientes", "em_andamento", "critica", fase2),
        ("Conseguir 10 clientes pagantes", "Segunda meta", "clientes_pagantes", 0, 10, "clientes", "nao_iniciado", "alta", fase3),
        ("Conseguir 20 clientes pagantes", "Terceira meta", "clientes_pagantes", 0, 20, "clientes", "nao_iniciado", "media", fase3),
        ("Conseguir 50 clientes pagantes", "Quarta meta", "clientes_pagantes", 0, 50, "clientes", "nao_iniciado", "media", fase8),
        ("Conseguir 100 clientes pagantes", "Quinta meta", "clientes_pagantes", 0, 100, "clientes", "nao_iniciado", "baixa", fase8),
    ]
    for m in metas:
        cur.execute("""INSERT INTO goals
            (titulo, descricao, indicador, valor_inicial, valor_meta, unidade, status, prioridade, fase_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", m)

    # Tarefas da meta dos 5 clientes
    cur.execute("SELECT id FROM goals WHERE titulo LIKE '%primeiros 5%'")
    goal1 = cur.fetchone()[0]

    tarefas = [
        ("Encontrar 20 empresas", "critica", "alto", "medio"),
        ("Fazer 20 contatos", "critica", "alto", "medio"),
        ("Fazer 5 demonstracoes", "critica", "alto", "medio"),
        ("Conseguir 10 testes", "alta", "alto", "medio"),
        ("Converter primeiro cliente", "critica", "alto", "alto"),
        ("Converter segundo cliente", "alta", "alto", "alto"),
        ("Converter terceiro cliente", "alta", "alto", "alto"),
        ("Converter quarto cliente", "media", "alto", "alto"),
        ("Converter quinto cliente", "media", "alto", "alto"),
    ]
    for t in tarefas:
        cur.execute("""INSERT INTO tasks
            (titulo, goal_id, status, prioridade, impacto, esforco)
            VALUES (%s, %s, 'pendente', %s, %s, %s)""", (t[0], goal1, t[1], t[2], t[3]))

    # Diario — entrada inicial
    cur.execute("""INSERT INTO journal_entries
        (titulo, conteudo, categoria, resultado, proximo_passo)
        VALUES (%s, %s, %s, %s, %s)""", (
        "Primeira versao do SaaS em producao",
        "Sistema M.A Tech Atendimento com IA funcionando no Render com banco no Supabase.",
        "produto",
        "Sistema funcionando.",
        "Conseguir primeiros usuarios e validar comercialmente."
    ))

    # Bloqueio inicial
    cur.execute("""INSERT INTO blockers
        (titulo, problema, impacto, status, prioridade, solucao_necessaria)
        VALUES (%s, %s, %s, 'aberto', 'critica', %s)""", (
        "Poucos usuarios ativos no teste",
        "O produto existe mas ainda nao tem base de usuarios suficiente para validar comercialmente.",
        "Travando a validacao comercial",
        "Conseguir mais usuarios gratuitos e converter para pagos."
    ))

    conn.commit()
    cur.close()
    close_conn(conn)
    print("Plano DB: tabelas e seeds OK")