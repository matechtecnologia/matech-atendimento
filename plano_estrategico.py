# plano_estrategico.py
# M.A Tech — Painel Estratégico
# FASE A: criação das tabelas
# Criado em: 01/10/2026

def inicializar_plano_estrategico(get_conn, close_conn):
    """Cria as tabelas do Painel Estratégico M.A Tech.
    Idempotente. Se der erro, NÃO derruba o app.
    """
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS strategic_plans (
            id SERIAL PRIMARY KEY,
            versao INTEGER NOT NULL DEFAULT 1,
            missao TEXT,
            visao TEXT,
            fase_atual TEXT,
            status TEXT DEFAULT 'em_execucao',
            data_inicio DATE DEFAULT CURRENT_DATE,
            data_fim_prevista DATE,
            data_fim_real DATE,
            observacoes TEXT,
            criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS roadmap_phases (
            id SERIAL PRIMARY KEY,
            numero INTEGER NOT NULL,
            nome TEXT NOT NULL,
            descricao TEXT,
            objetivo TEXT,
            status TEXT DEFAULT 'planejado',
            percentual INTEGER DEFAULT 0,
            data_prevista DATE,
            data_real DATE,
            dependencias TEXT,
            criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS goals (
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

        cur.execute("""CREATE TABLE IF NOT EXISTS tasks (
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

        cur.execute("""CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            descricao TEXT,
            tipo TEXT,
            status TEXT DEFAULT 'planejado',
            prioridade TEXT DEFAULT 'media',
            percentual INTEGER DEFAULT 0,
            data_inicio DATE,
            data_prevista DATE,
            data_real DATE,
            responsavel TEXT,
            observacao TEXT,
            criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            descricao TEXT,
            status TEXT DEFAULT 'planejado',
            problema_que_resolve TEXT,
            publico TEXT,
            solucao TEXT,
            modelo_negocio TEXT,
            prioridade TEXT DEFAULT 'media',
            custo_estimado NUMERIC,
            complexidade TEXT,
            potencial_receita NUMERIC,
            dependencias TEXT,
            fase_id INTEGER REFERENCES roadmap_phases(id) ON DELETE SET NULL,
            criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS metrics (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            categoria TEXT,
            valor NUMERIC DEFAULT 0,
            unidade TEXT,
            meta NUMERIC,
            data_referencia DATE DEFAULT CURRENT_DATE,
            observacao TEXT,
            criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS decisions (
            id SERIAL PRIMARY KEY,
            data_decisao DATE DEFAULT CURRENT_DATE,
            decisao TEXT NOT NULL,
            motivo TEXT,
            alternativas TEXT,
            impacto_esperado TEXT,
            resultado_real TEXT,
            status TEXT DEFAULT 'tomada',
            criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS blockers (
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
            resolvido_em TIMESTAMP WITH TIME ZONE,
            atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS journal_entries (
            id SERIAL PRIMARY KEY,
            data DATE DEFAULT CURRENT_DATE,
            titulo TEXT NOT NULL,
            conteudo TEXT,
            categoria TEXT,
            resultado TEXT,
            proximo_passo TEXT,
            criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS weekly_reports (
            id SERIAL PRIMARY KEY,
            semana_inicio DATE NOT NULL,
            semana_fim DATE NOT NULL,
            concluido TEXT,
            em_andamento TEXT,
            atrasado TEXT,
            resultados TEXT,
            problemas TEXT,
            metas TEXT,
            proximas_acoes TEXT,
            principal_gargalo TEXT,
            receita_gerada NUMERIC DEFAULT 0,
            clientes_conquistados INTEGER DEFAULT 0,
            decisoes_necessarias TEXT,
            criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS monthly_reports (
            id SERIAL PRIMARY KEY,
            mes INTEGER NOT NULL,
            ano INTEGER NOT NULL,
            receita NUMERIC DEFAULT 0,
            custos NUMERIC DEFAULT 0,
            lucro NUMERIC DEFAULT 0,
            clientes_total INTEGER DEFAULT 0,
            novos_clientes INTEGER DEFAULT 0,
            cancelamentos INTEGER DEFAULT 0,
            mrr NUMERIC DEFAULT 0,
            produtos TEXT,
            projetos TEXT,
            metas TEXT,
            execucao_percentual INTEGER DEFAULT 0,
            principais_resultados TEXT,
            principais_problemas TEXT,
            evolucao_vs_mes_anterior TEXT,
            criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(mes, ano)
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS revenue_records (
            id SERIAL PRIMARY KEY,
            data DATE DEFAULT CURRENT_DATE,
            tipo TEXT,
            descricao TEXT,
            valor NUMERIC NOT NULL,
            cliente TEXT,
            produto_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
            projeto_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
            status TEXT DEFAULT 'recebido',
            observacao TEXT,
            criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS plan_modules (
            id SERIAL PRIMARY KEY,
            projeto_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            modulo TEXT NOT NULL,
            ativo BOOLEAN DEFAULT TRUE,
            observacao TEXT,
            criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )""")

        cur.execute("CREATE INDEX IF NOT EXISTS idx_goals_status ON goals(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_goals_prioridade ON goals(prioridade)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tasks_goal ON tasks(goal_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tasks_fase ON tasks(fase_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tasks_projeto ON tasks(projeto_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_roadmap_numero ON roadmap_phases(numero)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_products_status ON products(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_metrics_categoria ON metrics(categoria)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_metrics_data ON metrics(data_referencia DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_decisions_data ON decisions(data_decisao DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_blockers_status ON blockers(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_journal_data ON journal_entries(data DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_revenue_data ON revenue_records(data DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_revenue_tipo ON revenue_records(tipo)")

        cur.execute("SELECT COUNT(*) FROM strategic_plans")
        if cur.fetchone()[0] == 0:
            cur.execute("""INSERT INTO strategic_plans
                (versao, missao, visao, fase_atual, status)
                VALUES (%s, %s, %s, %s, %s)""", (
                1,
                'A M.A Tech será uma empresa de tecnologia, gestão, atendimento, vendas e soluções empresariais com IA.',
                'Evoluir de uma empresa que vende ferramentas para uma empresa que estrutura, automatiza e gerencia processos empresariais através de tecnologia e IA.',
                'Validação comercial do M.A Tech Atendimento com IA',
                'em_execucao'
            ))

        cur.execute("SELECT COUNT(*) FROM roadmap_phases")
        if cur.fetchone()[0] == 0:
            fases = [
                (1, 'M.A Tech Atendimento com IA', 'Produto 01 construído e em produção', 'concluido', 100),
                (2, 'Validação comercial', 'Conseguir os primeiros 5 clientes pagantes', 'em_execucao', 0),
                (3, 'Primeiros clientes', 'Retenção e validação de preço', 'planejado', 0),
                (4, 'Produto em produção', 'Melhoria contínua do Atendimento', 'planejado', 0),
                (5, 'Plataforma de Gestão', 'Início do Produto 02 — M.A Tech Gestão', 'planejado', 0),
                (6, 'Gestão completa/específica', 'Módulos configuráveis por cliente', 'planejado', 0),
                (7, 'Integração Atendimento + Gestão', 'Unificar os dois produtos', 'planejado', 0),
                (8, 'Escala comercial', 'Aquisição em volume', 'planejado', 0),
                (9, 'Ecossistema M.A Tech', 'Ecossistema completo de soluções', 'planejado', 0),
            ]
            for f in fases:
                cur.execute("""INSERT INTO roadmap_phases
                    (numero, nome, descricao, status, percentual)
                    VALUES (%s, %s, %s, %s, %s)""", f)

        cur.execute("SELECT COUNT(*) FROM products")
        if cur.fetchone()[0] == 0:
            cur.execute("""INSERT INTO products
                (nome, descricao, status, prioridade)
                VALUES (%s, %s, %s, %s)""", (
                'M.A Tech Atendimento com IA',
                'Sistema de atendimento comercial com IA: recebe informações do negócio, cria IA personalizada, mantém histórico, analisa conversas, sugere o que falar, indica próximo passo.',
                'producao',
                'critica'
            ))
            cur.execute("""INSERT INTO products
                (nome, descricao, status, prioridade)
                VALUES (%s, %s, %s, %s)""", (
                'M.A Tech Gestão',
                'Plataforma para gestão empresarial através de tecnologia. Módulos configuráveis.',
                'planejado',
                'alta'
            ))

        cur.execute("SELECT COUNT(*) FROM goals")
        if cur.fetchone()[0] == 0:
            cur.execute("SELECT id FROM roadmap_phases WHERE numero = 2 LIMIT 1")
            r = cur.fetchone(); fase2 = r[0] if r else None
            cur.execute("SELECT id FROM roadmap_phases WHERE numero = 3 LIMIT 1")
            r = cur.fetchone(); fase3 = r[0] if r else None
            cur.execute("SELECT id FROM roadmap_phases WHERE numero = 8 LIMIT 1")
            r = cur.fetchone(); fase8 = r[0] if r else None

            metas = [
                ('Conseguir os primeiros 5 clientes pagantes', 'Primeira meta comercial', 'clientes_pagantes', 0, 0, 5, 'clientes', 'em_andamento', 'critica', fase2),
                ('Conseguir 10 clientes pagantes', 'Segunda meta', 'clientes_pagantes', 0, 0, 10, 'clientes', 'nao_iniciado', 'alta', fase3),
                ('Conseguir 20 clientes pagantes', 'Terceira meta', 'clientes_pagantes', 0, 0, 20, 'clientes', 'nao_iniciado', 'media', fase3),
                ('Conseguir 50 clientes pagantes', 'Quarta meta', 'clientes_pagantes', 0, 0, 50, 'clientes', 'nao_iniciado', 'media', fase8),
                ('Conseguir 100 clientes pagantes', 'Quinta meta', 'clientes_pagantes', 0, 0, 100, 'clientes', 'nao_iniciado', 'baixa', fase8),
            ]
            for m in metas:
                cur.execute("""INSERT INTO goals
                    (titulo, descricao, indicador, valor_inicial, valor_atual, valor_meta, unidade, status, prioridade, fase_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", m)

        cur.execute("SELECT COUNT(*) FROM tasks")
        if cur.fetchone()[0] == 0:
            cur.execute("SELECT id FROM goals WHERE titulo = 'Conseguir os primeiros 5 clientes pagantes' LIMIT 1")
            r = cur.fetchone(); g1 = r[0] if r else None
            if g1:
                tarefas = [
                    ('Encontrar 20 empresas', 'critica', 'alto', 'medio'),
                    ('Fazer 20 contatos', 'critica', 'alto', 'medio'),
                    ('Fazer 5 demonstrações', 'critica', 'alto', 'medio'),
                    ('Conseguir 10 testes', 'alta', 'alto', 'medio'),
                    ('Converter primeiro cliente', 'critica', 'alto', 'alto'),
                ]
                for t in tarefas:
                    cur.execute("""INSERT INTO tasks
                        (titulo, goal_id, status, prioridade, impacto, esforco)
                        VALUES (%s, %s, 'pendente', %s, %s, %s)""",
                        (t[0], g1, t[1], t[2], t[3]))

        cur.execute("SELECT COUNT(*) FROM journal_entries")
        if cur.fetchone()[0] == 0:
            cur.execute("""INSERT INTO journal_entries
                (titulo, conteudo, categoria, resultado, proximo_passo)
                VALUES (%s, %s, %s, %s, %s)""", (
                'Primeira versão do SaaS colocada em produção',
                'Sistema M.A Tech Atendimento com IA está funcionando em produção no Render com banco no Supabase.',
                'produto',
                'Sistema funcionando.',
                'Conseguir primeiros usuários e validar comercialmente.'
            ))

        conn.commit()
        cur.close()
        close_conn(conn)
        print("Plano Estrategico: tabelas OK")

    except Exception as e:
        print(f"Plano Estrategico: ERRO ao inicializar — {e}")