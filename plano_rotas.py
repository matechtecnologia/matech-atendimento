# plano_rotas.py
# M.A Tech — Painel Estratégico
# FASE B: rotas do painel
# Criado em: 01/10/2026
#
# IMPORTANTE: este arquivo NÃO importa nada de app.py.
# Recebe get_conn, close_conn, templates e helpers como parâmetro (evita import circular).


def registrar_rotas_plano(app, get_conn, close_conn, templates, Cookie, RedirectResponse, HTMLResponse, Request):
    """Registra as rotas /plano/* no app FastAPI."""

    from psycopg2.extras import RealDictCursor

    # ============================================================
    # HELPERS INTERNOS
    # ============================================================

    def _so_admin(usuario_tipo):
        return usuario_tipo == "admin"

    def _carregar_dashboard():
        """Carrega tudo que o dashboard precisa."""
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        dados = {}

        # Plano estratégico
        cur.execute("SELECT * FROM strategic_plans ORDER BY id LIMIT 1")
        dados["plano"] = cur.fetchone()

        # Fase atual (a que está em_execucao)
        cur.execute("SELECT * FROM roadmap_phases WHERE status = 'em_execucao' ORDER BY numero LIMIT 1")
        dados["fase_atual"] = cur.fetchone()

        # Meta atual (a primeira em_andamento)
        cur.execute("SELECT * FROM goals WHERE status = 'em_andamento' ORDER BY prioridade LIMIT 1")
        dados["meta_atual"] = cur.fetchone()

        # Contagem de produtos por status
        cur.execute("SELECT status, COUNT(*) as qtd FROM products GROUP BY status")
        dados["produtos_por_status"] = {r["status"]: r["qtd"] for r in cur.fetchall()}

        # Roadmap resumo
        cur.execute("SELECT status, COUNT(*) as qtd FROM roadmap_phases GROUP BY status")
        dados["roadmap_por_status"] = {r["status"]: r["qtd"] for r in cur.fetchall()}

        # Próxima ação (primeira tarefa pendente crítica, senão alta, senão qualquer)
        cur.execute("""
            SELECT t.*, g.titulo as goal_titulo
            FROM tasks t
            LEFT JOIN goals g ON g.id = t.goal_id
            WHERE t.status IN ('pendente','em_andamento')
            ORDER BY
                CASE t.prioridade
                    WHEN 'critica' THEN 1
                    WHEN 'alta' THEN 2
                    WHEN 'media' THEN 3
                    ELSE 4
                END,
                t.id
            LIMIT 1
        """)
        dados["proxima_acao"] = cur.fetchone()

        # Bloqueios abertos
        cur.execute("SELECT * FROM blockers WHERE status = 'aberto' ORDER BY prioridade, id LIMIT 1")
        dados["bloqueio_principal"] = cur.fetchone()

        cur.execute("SELECT COUNT(*) as t FROM blockers WHERE status = 'aberto'")
        dados["total_bloqueios"] = cur.fetchone()["t"]

        # Contadores reais do SaaS
        cur.execute("SELECT COUNT(*) as t FROM vendedores WHERE plano != 'gratis'")
        dados["clientes_pagantes"] = cur.fetchone()["t"]

        cur.execute("SELECT COUNT(*) as t FROM vendedores WHERE plano = 'gratis'")
        dados["usuarios_gratis"] = cur.fetchone()["t"]

        cur.execute("SELECT COUNT(*) as t FROM vendedores")
        dados["total_usuarios"] = cur.fetchone()["t"]

        # MRR (soma dos valores dos pagamentos pagos no mês atual)
        cur.execute("""
            SELECT COALESCE(SUM(valor), 0) as mrr
            FROM pagamentos
            WHERE status = 'pago'
              AND criado_em >= DATE_TRUNC('month', CURRENT_DATE)
        """)
        dados["mrr"] = float(cur.fetchone()["mrr"] or 0)

        # Metas ativas (para o card de meta)
        if dados["meta_atual"]:
            dados["meta_valor_atual"] = dados["meta_atual"]["valor_atual"]
            dados["meta_valor_meta"] = dados["meta_atual"]["valor_meta"]
            try:
                dados["meta_pct"] = int((float(dados["meta_valor_atual"]) / float(dados["meta_valor_meta"])) * 100) if dados["meta_valor_meta"] else 0
            except Exception:
                dados["meta_pct"] = 0
        else:
            dados["meta_valor_atual"] = 0
            dados["meta_valor_meta"] = 0
            dados["meta_pct"] = 0

        # Progresso do roadmap (média dos percentuais)
        cur.execute("SELECT AVG(percentual) as media FROM roadmap_phases")
        media = cur.fetchone()["media"]
        dados["roadmap_progresso"] = int(media) if media else 0

        # Contagem de tarefas por status
        cur.execute("SELECT status, COUNT(*) as qtd FROM tasks GROUP BY status")
        dados["tarefas_por_status"] = {r["status"]: r["qtd"] for r in cur.fetchall()}

        cur.close()
        close_conn(conn)
        return dados

    def _status_execucao(dados):
        """Calcula status geral: no caminho / atenção / atrasado."""
        total_tarefas = sum(dados["tarefas_por_status"].values()) or 1
        concluidas = dados["tarefas_por_status"].get("concluida", 0)
        pct_tarefas = int((concluidas / total_tarefas) * 100)

        bloqueios = dados.get("total_bloqueios", 0)
        pct_roadmap = dados.get("roadmap_progresso", 0)

        # Lógica simples: junta roadmap + tarefas, penaliza bloqueios
        base = (pct_roadmap + pct_tarefas) // 2
        if bloqueios >= 3:
            status = "atrasado"
            motivo = f"Existem {bloqueios} bloqueios abertos travando o avanço."
        elif bloqueios >= 1:
            status = "atencao"
            motivo = f"Existe {bloqueios} bloqueio aberto. Verificar antes de avançar."
        elif base >= 60:
            status = "no_caminho"
            motivo = "Roadmap e tarefas avançando conforme o planejado."
        elif base >= 30:
            status = "atencao"
            motivo = "Avanço abaixo do esperado. Revisar prioridades."
        else:
            status = "atrasado"
            motivo = "Execução muito baixa. Focar no que gera resultado primeiro."

        return {
            "pct": base,
            "status": status,
            "motivo": motivo,
            "pct_tarefas": pct_tarefas,
            "pct_roadmap": pct_roadmap,
        }

    # ============================================================
    # ROTAS
    # ============================================================

    @app.get("/plano", response_class=HTMLResponse)
    def plano_dashboard(
        request: Request,
        usuario_id: str = Cookie(None),
        usuario_nome: str = Cookie(None),
        usuario_tipo: str = Cookie(None),
    ):
        if not usuario_id or not _so_admin(usuario_tipo):
            return RedirectResponse(url="/login")

        dados = _carregar_dashboard()
        execucao = _status_execucao(dados)

        return templates.TemplateResponse(
            request=request,
            name="plano_dashboard.html",
            context={
                "usuario_nome": usuario_nome,
                "usuario_tipo": usuario_tipo,
                "ativo": "dashboard",
                "dados": dados,
                "execucao": execucao,
            },
        )

    @app.get("/plano/roadmap", response_class=HTMLResponse)
    def plano_roadmap(
        request: Request,
        usuario_id: str = Cookie(None),
        usuario_nome: str = Cookie(None),
        usuario_tipo: str = Cookie(None),
    ):
        if not usuario_id or not _so_admin(usuario_tipo):
            return RedirectResponse(url="/login")

        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM roadmap_phases ORDER BY numero")
        fases = [dict(f) for f in cur.fetchall()]
        cur.close()
        close_conn(conn)

        return templates.TemplateResponse(
            request=request,
            name="plano_roadmap.html",
            context={
                "usuario_nome": usuario_nome,
                "usuario_tipo": usuario_tipo,
                "ativo": "roadmap",
                "fases": fases,
            },
        )

    @app.get("/plano/metas", response_class=HTMLResponse)
    def plano_metas(
        request: Request,
        usuario_id: str = Cookie(None),
        usuario_nome: str = Cookie(None),
        usuario_tipo: str = Cookie(None),
    ):
        if not usuario_id or not _so_admin(usuario_tipo):
            return RedirectResponse(url="/login")

        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM goals ORDER BY prioridade, id")
        metas = []
        for m in cur.fetchall():
            m = dict(m)
            try:
                if float(m["valor_meta"]) > 0:
                    m["pct"] = int((float(m["valor_atual"]) / float(m["valor_meta"])) * 100)
                else:
                    m["pct"] = 0
            except Exception:
                m["pct"] = 0
            metas.append(m)
        cur.close()
        close_conn(conn)

        return templates.TemplateResponse(
            request=request,
            name="plano_metas.html",
            context={
                "usuario_nome": usuario_nome,
                "usuario_tipo": usuario_tipo,
                "ativo": "metas",
                "metas": metas,
            },
        )

    @app.get("/plano/tarefas", response_class=HTMLResponse)
    def plano_tarefas(
        request: Request,
        usuario_id: str = Cookie(None),
        usuario_nome: str = Cookie(None),
        usuario_tipo: str = Cookie(None),
    ):
        if not usuario_id or not _so_admin(usuario_tipo):
            return RedirectResponse(url="/login")

        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT t.*, g.titulo as goal_titulo
            FROM tasks t
            LEFT JOIN goals g ON g.id = t.goal_id
            ORDER BY
                CASE t.status WHEN 'em_andamento' THEN 1 WHEN 'pendente' THEN 2 ELSE 3 END,
                CASE t.prioridade
                    WHEN 'critica' THEN 1
                    WHEN 'alta' THEN 2
                    WHEN 'media' THEN 3
                    ELSE 4
                END,
                t.id
        """)
        tarefas = [dict(t) for t in cur.fetchall()]
        cur.close()
        close_conn(conn)

        return templates.TemplateResponse(
            request=request,
            name="plano_tarefas.html",
            context={
                "usuario_nome": usuario_nome,
                "usuario_tipo": usuario_tipo,
                "ativo": "tarefas",
                "tarefas": tarefas,
            },
        )

    @app.get("/plano/diario", response_class=HTMLResponse)
    def plano_diario(
        request: Request,
        usuario_id: str = Cookie(None),
        usuario_nome: str = Cookie(None),
        usuario_tipo: str = Cookie(None),
    ):
        if not usuario_id or not _so_admin(usuario_tipo):
            return RedirectResponse(url="/login")

        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM journal_entries ORDER BY data DESC, id DESC")
        entradas = [dict(e) for e in cur.fetchall()]
        cur.close()
        close_conn(conn)

        return templates.TemplateResponse(
            request=request,
            name="plano_diario.html",
            context={
                "usuario_nome": usuario_nome,
                "usuario_tipo": usuario_tipo,
                "ativo": "diario",
                "entradas": entradas,
            },
        )