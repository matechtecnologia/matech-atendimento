# plano_rotas.py
# M.A Tech â€” Painel EstratÃ©gico
# FASE B+C: leitura + ediÃ§Ã£o
# Atualizado em: 01/10/2026

from fastapi import Form
from fastapi.responses import RedirectResponse
import plano_sync


def registrar_rotas_plano(app, get_conn, close_conn, templates, Cookie, RedirectResponse, HTMLResponse, Request):
    """Registra as rotas /plano/* no app FastAPI."""

    from psycopg2.extras import RealDictCursor

    def _so_admin(usuario_tipo):
        return usuario_tipo == "admin"

    def _carregar_dashboard():
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        dados = {}

        cur.execute("SELECT * FROM strategic_plans ORDER BY id LIMIT 1")
        dados["plano"] = cur.fetchone()

        cur.execute("SELECT * FROM roadmap_phases WHERE status = 'em_execucao' ORDER BY numero LIMIT 1")
        dados["fase_atual"] = cur.fetchone()

        cur.execute("SELECT * FROM goals WHERE status = 'em_andamento' ORDER BY prioridade LIMIT 1")
        dados["meta_atual"] = cur.fetchone()

        cur.execute("SELECT status, COUNT(*) as qtd FROM products GROUP BY status")
        dados["produtos_por_status"] = {r["status"]: r["qtd"] for r in cur.fetchall()}

        cur.execute("SELECT status, COUNT(*) as qtd FROM roadmap_phases GROUP BY status")
        dados["roadmap_por_status"] = {r["status"]: r["qtd"] for r in cur.fetchall()}

        cur.execute("""
            SELECT t.*, g.titulo as goal_titulo
            FROM tasks t
            LEFT JOIN goals g ON g.id = t.goal_id
            WHERE t.status IN ('pendente','em_andamento')
            ORDER BY
                CASE t.prioridade
                    WHEN 'critica' THEN 1 WHEN 'alta' THEN 2
                    WHEN 'media' THEN 3 ELSE 4
                END,
                t.id
            LIMIT 1
        """)
        dados["proxima_acao"] = cur.fetchone()

        cur.execute("SELECT * FROM blockers WHERE status = 'aberto' ORDER BY prioridade, id LIMIT 1")
        dados["bloqueio_principal"] = cur.fetchone()

        cur.execute("SELECT COUNT(*) as t FROM blockers WHERE status = 'aberto'")
        dados["total_bloqueios"] = cur.fetchone()["t"]

        cur.execute("SELECT COUNT(*) as t FROM vendedores WHERE plano != 'gratis'")
        dados["clientes_pagantes"] = cur.fetchone()["t"]

        cur.execute("SELECT COUNT(*) as t FROM vendedores WHERE plano = 'gratis'")
        dados["usuarios_gratis"] = cur.fetchone()["t"]

        cur.execute("SELECT COUNT(*) as t FROM vendedores")
        dados["total_usuarios"] = cur.fetchone()["t"]

        cur.execute("""
            SELECT COALESCE(SUM(valor), 0) as mrr
            FROM pagamentos
            WHERE status = 'pago'
              AND criado_em >= DATE_TRUNC('month', CURRENT_DATE)
        """)
        dados["mrr"] = float(cur.fetchone()["mrr"] or 0)

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

        cur.execute("SELECT AVG(percentual) as media FROM roadmap_phases")
        media = cur.fetchone()["media"]
        dados["roadmap_progresso"] = int(media) if media else 0

        cur.execute("SELECT status, COUNT(*) as qtd FROM tasks GROUP BY status")
        dados["tarefas_por_status"] = {r["status"]: r["qtd"] for r in cur.fetchall()}

        cur.close()
        close_conn(conn)
        return dados

    def _status_execucao(dados):
        total_tarefas = sum(dados["tarefas_por_status"].values()) or 1
        concluidas = dados["tarefas_por_status"].get("concluida", 0)
        pct_tarefas = int((concluidas / total_tarefas) * 100)

        bloqueios = dados.get("total_bloqueios", 0)
        pct_roadmap = dados.get("roadmap_progresso", 0)

        base = (pct_roadmap + pct_tarefas) // 2
        if bloqueios >= 3:
            status = "atrasado"
            motivo = f"Existem {bloqueios} bloqueios abertos travando o Avanco."
        elif bloqueios >= 1:
            status = "atencao"
            motivo = f"Existe {bloqueios} bloqueio aberto. Verificar antes de avancar."
        elif base >= 60:
            status = "no_caminho"
            motivo = "Roadmap e tarefas avanÃ§ando conforme o planejado."
        elif base >= 30:
            status = "atencao"
            motivo = "Avanco abaixo do esperado. Revisar prioridades."
        else:
            status = "atrasado"
            motivo = "Execucao muito baixa. Focar no que gera resultado primeiro."

        return {"pct": base, "status": status, "motivo": motivo, "pct_tarefas": pct_tarefas, "pct_roadmap": pct_roadmap}

    # ============================================================
    # LEITURA
    # ============================================================

    @app.get("/plano", response_class=HTMLResponse)
    def plano_dashboard(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None), ok: str = None):
        if not usuario_id or not _so_admin(usuario_tipo):
            return RedirectResponse(url="/login")
        dados = _carregar_dashboard()
        execucao = _status_execucao(dados)
        return templates.TemplateResponse(request=request, name="plano_dashboard.html", context={
            "usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo, "ativo": "dashboard",
            "dados": dados, "execucao": execucao, "ok": ok,
        })

    @app.get("/plano/roadmap", response_class=HTMLResponse)
    def plano_roadmap(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None), ok: str = None):
        if not usuario_id or not _so_admin(usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM roadmap_phases ORDER BY numero")
        fases = [dict(f) for f in cur.fetchall()]
        cur.close()
        close_conn(conn)
        return templates.TemplateResponse(request=request, name="plano_roadmap.html", context={
            "usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo, "ativo": "roadmap",
            "fases": fases, "ok": ok,
        })

    @app.get("/plano/metas", response_class=HTMLResponse)
    def plano_metas(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None), ok: str = None):
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
        return templates.TemplateResponse(request=request, name="plano_metas.html", context={
            "usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo, "ativo": "metas",
            "metas": metas, "ok": ok,
        })

    @app.get("/plano/tarefas", response_class=HTMLResponse)
    def plano_tarefas(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None), ok: str = None):
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
                CASE t.prioridade WHEN 'critica' THEN 1 WHEN 'alta' THEN 2 WHEN 'media' THEN 3 ELSE 4 END,
                t.id
        """)
        tarefas = [dict(t) for t in cur.fetchall()]
        cur.execute("SELECT id, titulo FROM goals ORDER BY id")
        metas = [dict(g) for g in cur.fetchall()]
        cur.close()
        close_conn(conn)
        return templates.TemplateResponse(request=request, name="plano_tarefas.html", context={
            "usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo, "ativo": "tarefas",
            "tarefas": tarefas, "metas": metas, "ok": ok,
        })

    @app.get("/plano/diario", response_class=HTMLResponse)
    def plano_diario(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None), ok: str = None):
        if not usuario_id or not _so_admin(usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM journal_entries ORDER BY data DESC, id DESC")
        entradas = [dict(e) for e in cur.fetchall()]
        cur.close()
        close_conn(conn)
        return templates.TemplateResponse(request=request, name="plano_diario.html", context={
            "usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo, "ativo": "diario",
            "entradas": entradas, "ok": ok,
        })

    # ============================================================
    # EDIÃ‡ÃƒO â€” TAREFAS
    # ============================================================

    @app.post("/plano/tarefa/{tarefa_id}/concluir")
    def tarefa_concluir(tarefa_id: int, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not usuario_id or not _so_admin(usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE tasks SET status='concluida', concluida_em=CURRENT_TIMESTAMP, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s", (tarefa_id,))
        conn.commit()
        cur.close()
        close_conn(conn)
        return RedirectResponse(url="/plano/tarefas?ok=1", status_code=303)

    @app.post("/plano/tarefa/{tarefa_id}/reabrir")
    def tarefa_reabrir(tarefa_id: int, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not usuario_id or not _so_admin(usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE tasks SET status='pendente', concluida_em=NULL, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s", (tarefa_id,))
        conn.commit()
        cur.close()
        close_conn(conn)
        return RedirectResponse(url="/plano/tarefas?ok=1", status_code=303)

    @app.post("/plano/tarefa/criar")
    def tarefa_criar(
        titulo: str = Form(...),
        descricao: str = Form(""),
        goal_id: str = Form(""),
        prioridade: str = Form("media"),
        impacto: str = Form(""),
        esforco: str = Form(""),
        usuario_id: str = Cookie(None),
        usuario_tipo: str = Cookie(None),
    ):
        if not usuario_id or not _so_admin(usuario_tipo):
            return RedirectResponse(url="/login")
        gid = int(goal_id) if goal_id and goal_id.isdigit() else None
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO tasks (titulo, descricao, goal_id, status, prioridade, impacto, esforco)
            VALUES (%s, %s, %s, 'pendente', %s, %s, %s)
        """, (titulo, descricao, gid, prioridade, impacto, esforco))
        conn.commit()
        cur.close()
        close_conn(conn)
        return RedirectResponse(url="/plano/tarefas?ok=1", status_code=303)

    @app.post("/plano/tarefa/{tarefa_id}/excluir")
    def tarefa_excluir(tarefa_id: int, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not usuario_id or not _so_admin(usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id=%s", (tarefa_id,))
        conn.commit()
        cur.close()
        close_conn(conn)
        return RedirectResponse(url="/plano/tarefas?ok=1", status_code=303)

    # ============================================================
    # EDIÃ‡ÃƒO â€” METAS
    # ============================================================

    @app.post("/plano/meta/{meta_id}/atualizar")
    def meta_atualizar(
        meta_id: int,
        valor_atual: str = Form(...),
        status: str = Form(""),
        usuario_id: str = Cookie(None),
        usuario_tipo: str = Cookie(None),
    ):
        if not usuario_id or not _so_admin(usuario_tipo):
            return RedirectResponse(url="/login")
        try:
            v = float(valor_atual.replace(",", "."))
        except Exception:
            return RedirectResponse(url="/plano/metas?ok=0", status_code=303)
        conn = get_conn()
        cur = conn.cursor()
        if status:
            cur.execute("UPDATE goals SET valor_atual=%s, status=%s, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s", (v, status, meta_id))
        else:
            cur.execute("UPDATE goals SET valor_atual=%s, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s", (v, meta_id))
        conn.commit()
        cur.close()
        close_conn(conn)
        return RedirectResponse(url="/plano/metas?ok=1", status_code=303)

    # ============================================================
    # EDIÃ‡ÃƒO â€” DIÃRIO
    # ============================================================

    @app.post("/plano/diario/criar")
    def diario_criar(
        titulo: str = Form(...),
        conteudo: str = Form(""),
        categoria: str = Form(""),
        resultado: str = Form(""),
        proximo_passo: str = Form(""),
        usuario_id: str = Cookie(None),
        usuario_tipo: str = Cookie(None),
    ):
        if not usuario_id or not _so_admin(usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO journal_entries (titulo, conteudo, categoria, resultado, proximo_passo)
            VALUES (%s, %s, %s, %s, %s)
        """, (titulo, conteudo, categoria, resultado, proximo_passo))
        conn.commit()
        cur.close()
        close_conn(conn)
        return RedirectResponse(url="/plano/diario?ok=1", status_code=303)

    # ============================================================
    # EDIÃ‡ÃƒO â€” ROADMAP
    # ============================================================

    @app.post("/plano/fase/{fase_id}/atualizar")
    def fase_atualizar(
        fase_id: int,
        status: str = Form(...),
        percentual: str = Form("0"),
        usuario_id: str = Cookie(None),
        usuario_tipo: str = Cookie(None),
    ):
        if not usuario_id or not _so_admin(usuario_tipo):
            return RedirectResponse(url="/login")
        try:
            pct = int(percentual)
            pct = max(0, min(100, pct))
        except Exception:
            pct = 0
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE roadmap_phases SET status=%s, percentual=%s, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s", (status, pct, fase_id))
        conn.commit()
        cur.close()
        close_conn(conn)
        return RedirectResponse(url="/plano/roadmap?ok=1", status_code=303)
    # ============================================================
    # SYNC AUTOMATICO
    # ============================================================

    @app.post("/plano/sync")
    def plano_sync_manual(usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not usuario_id or not _so_admin(usuario_tipo):
            return RedirectResponse(url="/login")
        try:
            resumo = plano_sync.executar_sync(app, get_conn, close_conn)
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO journal_entries (titulo, conteudo, categoria) VALUES (%s, %s, %s)",
                ("Sync manual",
                 f"Tarefas: {len(resumo['tarefas_concluidas'])} concluidas, {len(resumo['tarefas_criadas'])} criadas. "
                 f"Metas: {len(resumo['metas_atualizadas'])}. Fases: {len(resumo['fases_atualizadas'])}.",
                 "produto")
            )
            conn.commit()
            cur.close()
            close_conn(conn)
        except Exception as e:
            print(f"Erro sync manual: {e}")
        return RedirectResponse(url="/plano?ok=sync", status_code=303)

    @app.get("/plano/sync-cron")
    def plano_sync_cron(token: str = ""):
        import os as _os
        from fastapi.responses import JSONResponse
        token_esperado = _os.getenv("BACKUP_TOKEN", "")
        if not token_esperado or token != token_esperado:
            return JSONResponse({"erro": "token invalido"}, status_code=403)
        try:
            resumo = plano_sync.executar_sync(app, get_conn, close_conn)
            return {"status": "ok", "resumo": resumo}
        except Exception as e:
            return {"status": "erro", "msg": str(e)}

