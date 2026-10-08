# plano_ui.py
# M.A Tech — Interface do Painel (HTML + rotas)
# Gera o HTML dentro do codigo. Nao usa templates externos.

from fastapi import Form
from fastapi.responses import RedirectResponse, HTMLResponse


CSS = """
body { background:#0a0a0a; color:#e8e8e8; font-family:-apple-system,BlinkMacSystemFont,sans-serif; margin:0; }
.topo { background:#0f1a15; padding:14px 20px; border-bottom:1px solid #00d97e33; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; }
.topo h1 { color:#00d97e; font-size:18px; margin:0; }
.menu { display:flex; gap:12px; flex-wrap:wrap; }
.menu a { color:#e8e8e8; text-decoration:none; font-size:13px; padding:6px 10px; border-radius:6px; }

.grupo { display:flex; gap:6px; align-items:center; padding:2px 8px; border-right:1px solid #2a2a2a; }
.grupo:last-child { border-right:none; }
.grupo-label { color:#5a5a5a; font-size:9px; font-weight:700; letter-spacing:1px; margin-right:4px; text-transform:uppercase; }

.menu a:hover, .menu a.ativo { background:#00d97e22; color:#00d97e; }
.container { max-width:1100px; margin:20px auto; padding:0 20px; }
.cards { display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:12px; margin-bottom:20px; }
.card { background:#141414; border:1px solid #222; border-radius:8px; padding:14px; }
.card h3 { color:#8a8a8a; font-size:11px; text-transform:uppercase; margin:0 0 6px 0; letter-spacing:.5px; }
.card .v { color:#00d97e; font-size:24px; font-weight:700; font-family:monospace; }
.card .sub { color:#5a5a5a; font-size:11px; margin-top:4px; }
.bloco { background:#141414; border:1px solid #222; border-radius:8px; padding:18px; margin-bottom:14px; }
.bloco h2 { font-size:15px; margin:0 0 10px 0; color:#e8e8e8; }
.barra { height:8px; background:#2a2a2a; border-radius:4px; overflow:hidden; margin-top:8px; }
.barra-p { height:100%; background:#00d97e; }
.badge { display:inline-block; padding:3px 8px; border-radius:10px; font-size:10px; font-weight:700; text-transform:uppercase; }
.b-verde { background:#0a1f15; color:#00d97e; border:1px solid #00d97e; }
.b-amarelo { background:#1f1a0a; color:#f5c542; border:1px solid #f5c542; }
.b-vermelho { background:#1f0a0a; color:#ff5555; border:1px solid #ff5555; }
.b-cinza { background:#1a1a1a; color:#8a8a8a; border:1px solid #3a3a3a; }
.btn { display:inline-block; padding:8px 14px; border-radius:6px; font-size:12px; font-weight:700; cursor:pointer; font-family:inherit; border:1px solid; text-decoration:none; margin-right:6px; margin-top:6px; }
.btn-verde { background:#00d97e; color:#0a0a0a; border-color:#00d97e; }
.btn-cinza { background:#1a1a1a; color:#8a8a8a; border-color:#2a2a2a; }
.btn-vermelho { background:transparent; color:#ff5555; border-color:#ff5555; }
.btn-azul { background:#3b82f6; color:#fff; border-color:#3b82f6; }
.aviso { background:#0a1f15; border-left:3px solid #00d97e; padding:10px; border-radius:6px; margin-bottom:14px; color:#00d97e; font-size:13px; }
.texto-cinza { color:#8a8a8a; font-size:13px; }
.tarefa { background:#141414; border:1px solid #222; border-left:3px solid #00d97e; border-radius:8px; padding:14px; margin-bottom:10px; }
.tarefa.critica { border-left-color:#ff5555; }
.tarefa.alta { border-left-color:#f5c542; }
.tarefa.concluida { opacity:.5; }
.tarefa.concluida h2 { text-decoration:line-through; }
.tarefa h2 { font-size:14px; margin:0 0 6px 0; }
.tarefa p { color:#8a8a8a; font-size:12px; margin:3px 0; }
.form-inline { display:flex; gap:8px; flex-wrap:wrap; margin-top:10px; padding-top:10px; border-top:1px solid #2a2a2a; align-items:flex-end; }
.form-inline input, .form-inline select, .form-inline textarea { background:#0a0a0a; border:1px solid #2a2a2a; color:#fff; padding:8px 10px; border-radius:6px; font-size:13px; font-family:inherit; }
.form-inline label { color:#8a8a8a; font-size:11px; display:block; margin-bottom:3px; }
details summary { cursor:pointer; color:#00d97e; font-weight:700; padding:10px; background:#0f1a15; border-radius:6px; margin-bottom:14px; list-style:none; }
details summary::-webkit-details-marker { display:none; }
details[open] summary { border-radius:6px 6px 0 0; }
.form-box { background:#0f1a15; border:1px solid #00d97e; border-radius:0 0 8px 8px; padding:14px; margin-bottom:14px; }
.form-box input, .form-box select, .form-box textarea { width:100%; box-sizing:border-box; background:#0a0a0a; border:1px solid #2a2a2a; color:#fff; padding:9px; border-radius:6px; font-size:13px; font-family:inherit; margin-bottom:8px; }
.form-box label { color:#8a8a8a; font-size:11px; display:block; margin-bottom:3px; }
.fase { background:#141414; border:1px solid #222; border-left:3px solid #5a5a5a; border-radius:8px; padding:16px; margin-bottom:12px; }
.fase.concluido { border-left-color:#00d97e; }
.fase.em_execucao { border-left-color:#f5c542; }
.fase h2 { font-size:14px; margin:0 0 6px 0; }
.fase p { color:#8a8a8a; font-size:12px; margin:4px 0; }
.diario-item { background:#141414; border:1px solid #222; border-left:3px solid #00d97e; border-radius:8px; padding:14px; margin-bottom:10px; }
.diario-item h3 { font-size:14px; margin:0 0 4px 0; color:#e8e8e8; }
.diario-item .data { color:#5a5a5a; font-size:11px; font-family:monospace; }
.diario-item p { color:#c8c8c8; font-size:13px; margin:6px 0 0 0; }
.diario-item .res { color:#00d97e; font-size:12px; margin-top:6px; }
.diario-item .prox { color:#f5c542; font-size:12px; margin-top:4px; }
"""


def _auth(usuario_id, usuario_tipo):
    return usuario_id and usuario_tipo == "admin"


def _topo(ativo):
    grupos = [
        ("PAINEL", [
            ("/plano", "Dashboard", "dashboard"),
            ("/plano/fases", "Roadmap", "fases"),
            ("/plano/metas", "Metas", "metas"),
            ("/plano/tarefas", "Tarefas", "tarefas"),
        ]),
        ("PRODUTO", [
            ("/plano/produtos", "Produtos", "produtos"),
            ("/plano/projetos", "Projetos", "projetos"),
            ("/plano/lab", "Lab", "lab"),
            ("/plano/decisoes", "Decisoes", "decisoes"),
        ]),
        ("OPERACAO", [
            ("/plano/comercial", "Comercial", "comercial"),
            ("/plano/gestao", "Gestao", "gestao"),
            ("/plano/financeiro", "Financeiro", "financeiro"),
            ("/plano/roi", "ROI", "roi"),
            ("/plano/relatorios", "Relatorios", "relatorios"),
        ]),
        ("SISTEMA", [
            ("/plano/bloqueios", "Bloqueios", "bloqueios"),
            ("/plano/pendencias", "Pendencias", "pendencias"),
            ("/plano/proximos", "Proximos", "proximos"),
            ("/plano/diario", "Diario", "diario"),
        ]),
    ]
    partes = []
    for nome_grupo, itens in grupos:
        links = "".join(
            f'<a href="{href}" class="{"ativo" if ativo==key else ""}">{nome}</a>'
            for href, nome, key in itens
        )
        partes.append(f'<div class="grupo"><span class="grupo-label">{nome_grupo}</span>{links}</div>')
    menu = "".join(partes)
    return f"""
    <div class="topo">
        <h1>Plano M.A Tech</h1>
        <form method="POST" action="/plano/sync" style="margin:0;">
            <button type="submit" style="background:#00d97e;color:#0a0a0a;border:none;padding:8px 16px;border-radius:6px;font-weight:700;cursor:pointer;font-size:12px;">SINCRONIZAR</button>
        </form>
        <div class="menu">{menu}<a href="/admin/dashboard">Admin</a></div>
    </div>
    """


def _html(titulo, corpo):
    return f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titulo}</title><style>{CSS}</style></head>
<body>{corpo}</body></html>"""


def registrar_rotas_plano_ui(app, get_conn, close_conn, Cookie, Request):
    from psycopg2.extras import RealDictCursor
    import plano_core

    # ============================================================
    # DASHBOARD
    # ============================================================
    @app.get("/plano", response_class=HTMLResponse)
    def plano_dash(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None), ok: str = None):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")

        d = plano_core.carregar_dashboard(get_conn, close_conn)
        ex = plano_core.calcular_execucao(d)

        aviso = '<div class="aviso">Sincronizacao executada com sucesso.</div>' if ok == "sync" else ""

        fase_nome = d["fase_atual"]["nome"] if d.get("fase_atual") else "Sem fase"
        fase_desc = d["fase_atual"]["descricao"] if d.get("fase_atual") else ""

        meta_atual_txt = "—"
        meta_pct = d.get("meta_pct", 0)
        if d.get("meta_atual"):
            meta_atual_txt = d["meta_atual"]["titulo"]
            meta_valor = f'{d["meta_atual"]["valor_atual"]:.0f}/{d["meta_atual"]["valor_meta"]:.0f}'
        else:
            meta_valor = "0/0"

        prox = ""
        if d.get("proxima_acao"):
            pa = d["proxima_acao"]
            gtxt = f'<p class="texto-cinza">Meta: {pa["goal_titulo"]}</p>' if pa.get("goal_titulo") else ""
            prox = f"""
            <div class="bloco" style="border-left:3px solid #00d97e;">
                <h2>PROXIMA ACAO</h2>
                <p style="font-size:16px;margin:6px 0;">{pa["titulo"]}</p>
                {gtxt}
                <a href="/plano/tarefas" class="btn btn-verde" style="margin-top:8px;">EXECUTAR</a>
            </div>"""

        bloq = ""
        if d.get("bloqueio_principal"):
            b = d["bloqueio_principal"]
            bloq = f"""
            <div class="bloco" style="border-left:3px solid #ff5555;">
                <h2>PRINCIPAL BLOQUEIO</h2>
                <p style="font-size:15px;margin:6px 0;">{b["titulo"]}</p>
                <p class="texto-cinza">{b.get("problema") or ""}</p>
            </div>"""

        badge_status = {"no_caminho":"b-verde","atencao":"b-amarelo","atrasado":"b-vermelho"}.get(ex["status"],"b-cinza")

        corpo = f"""
        {_topo("dashboard")}
        <div class="container">
            {aviso}
            <div class="bloco">
                <div class="texto-cinza">FASE ATUAL</div>
                <h2 style="font-size:18px;color:#00d97e;margin:4px 0 0 0;">{fase_nome}</h2>
                <p class="texto-cinza">{fase_desc}</p>
            </div>
            <div class="bloco">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <h2 style="margin:0;">EXECUCAO DO PLANO</h2>
                    <span class="badge {badge_status}">{ex["status"].replace("_"," ").upper()}</span>
                </div>
                <div style="font-size:30px;font-family:monospace;color:#00d97e;margin-top:10px;">{ex["pct"]}%</div>
                <div class="barra"><div class="barra-p" style="width:{ex["pct"]}%;"></div></div>
                <p class="texto-cinza" style="margin-top:10px;">{ex["motivo"]}</p>
                <p class="texto-cinza" style="margin-top:6px;font-size:11px;">
                    Fases: {ex["fases_pct"]}% · Tarefas: {ex["tarefas_pct"]}% · Meta: {ex["meta_pct"]}%
                </p>
            </div>
            <div class="cards">
                <div class="card"><h3>MRR</h3><div class="v">R$ {d["mrr"]:.2f}</div></div>
                <div class="card"><h3>Clientes Pagantes</h3><div class="v">{d["clientes_pagantes"]}</div></div>
                <div class="card"><h3>Usuarios Gratis</h3><div class="v">{d["usuarios_gratis"]}</div></div>
                <div class="card"><h3>Total Usuarios</h3><div class="v">{d["total_usuarios"]}</div></div>
                <div class="card"><h3>Meta Atual</h3><div class="v" style="font-size:16px;">{meta_valor}</div><div class="sub">{meta_atual_txt[:40]}</div></div>
                <div class="card"><h3>Bloqueios</h3><div class="v">{d["total_bloqueios"]}</div></div>
                <div class="card"><h3>Leads</h3><div class="v">{d["leads"]}</div></div>
                <div class="card"><h3>Atendimentos</h3><div class="v">{d["atendimentos"]}</div></div>
            </div>
            {prox}
            {bloq}
        </div>
        """
        return HTMLResponse(_html("Plano M.A Tech", corpo))

    # ============================================================
    # ROADMAP / FASES
    # ============================================================
    @app.get("/plano/fases", response_class=HTMLResponse)
    def plano_fases(request: Request, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM roadmap_phases ORDER BY numero")
        fases = [dict(f) for f in cur.fetchall()]
        cur.close()
        close_conn(conn)

        html_fases = ""
        for f in fases:
            badge = {"concluido":"b-verde","em_execucao":"b-amarelo","validado":"b-verde","bloqueado":"b-vermelho"}.get(f["status"],"b-cinza")
            html_fases += f"""
            <div class="fase {f["status"]}">
                <h2>FASE {f["numero"]} — {f["nome"]} <span class="badge {badge}" style="float:right;">{f["status"]}</span></h2>
                <p>{f.get("descricao") or ""}</p>
                <div class="barra"><div class="barra-p" style="width:{f["percentual"]}%;"></div></div>
                <p style="text-align:right;color:#00d97e;font-family:monospace;font-size:12px;">{f["percentual"]}%</p>
                <form method="POST" action="/plano/fase/{f["id"]}/atualizar" class="form-inline">
                    <div><label>Status</label><select name="status">
                        <option value="planejado" {"selected" if f["status"]=="planejado" else ""}>Planejado</option>
                        <option value="em_execucao" {"selected" if f["status"]=="em_execucao" else ""}>Em execucao</option>
                        <option value="concluido" {"selected" if f["status"]=="concluido" else ""}>Concluido</option>
                        <option value="bloqueado" {"selected" if f["status"]=="bloqueado" else ""}>Bloqueado</option>
                    </select></div>
                    <div><label>Progresso %</label><input type="number" name="percentual" value="{f["percentual"]}" min="0" max="100" style="width:70px;"></div>
                    <button class="btn btn-verde" type="submit">SALVAR</button>
                </form>
            </div>"""
        corpo = f'{_topo("fases")}<div class="container">{html_fases}</div>'
        return HTMLResponse(_html("Roadmap", corpo))

    # ============================================================
    # METAS
    # ============================================================
    @app.get("/plano/metas", response_class=HTMLResponse)
    def plano_metas(request: Request, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None), ok: str = None):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM goals ORDER BY id")
        metas = [dict(m) for m in cur.fetchall()]
        cur.close()
        close_conn(conn)

        html_metas = ""
        for m in metas:
            try:
                va = float(m["valor_atual"] or 0); vm = float(m["valor_meta"] or 1)
                pct = int((va/vm)*100) if vm else 0
            except Exception:
                pct = 0
            badge = {"em_andamento":"b-amarelo","validado":"b-verde","concluido":"b-verde","bloqueado":"b-vermelho"}.get(m["status"],"b-cinza")
            html_metas += f"""
            <div class="bloco">
                <h2>{m["titulo"]} <span class="badge {badge}" style="float:right;">{m["status"]}</span></h2>
                <p class="texto-cinza">{m.get("descricao") or ""}</p>
                <div style="font-family:monospace;color:#00d97e;font-size:14px;margin-top:6px;">
                    {m["valor_atual"]:.0f} / {m["valor_meta"]:.0f} {m.get("unidade") or ""} ({pct}%)
                </div>
                <div class="barra"><div class="barra-p" style="width:{pct}%;"></div></div>
                <form method="POST" action="/plano/meta/{m["id"]}/atualizar" class="form-inline">
                    <div><label>Valor atual</label><input type="text" name="valor_atual" value="{m["valor_atual"]:.0f}" style="width:80px;"></div>
                    <div><label>Status</label><select name="status">
                        <option value="nao_iniciado" {"selected" if m["status"]=="nao_iniciado" else ""}>Nao iniciado</option>
                        <option value="em_andamento" {"selected" if m["status"]=="em_andamento" else ""}>Em andamento</option>
                        <option value="validado" {"selected" if m["status"]=="validado" else ""}>Validado</option>
                        <option value="bloqueado" {"selected" if m["status"]=="bloqueado" else ""}>Bloqueado</option>
                    </select></div>
                    <button class="btn btn-verde" type="submit">SALVAR</button>
                </form>
            </div>"""
        corpo = f'{_topo("metas")}<div class="container">{html_metas}</div>'
        return HTMLResponse(_html("Metas", corpo))

    # ============================================================
    # TAREFAS
    # ============================================================
    @app.get("/plano/tarefas", response_class=HTMLResponse)
    def plano_tarefas(request: Request, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None), ok: str = None):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""SELECT t.*, g.titulo as goal_titulo FROM tasks t
                       LEFT JOIN goals g ON g.id=t.goal_id
                       ORDER BY CASE t.status WHEN 'em_andamento' THEN 1 WHEN 'pendente' THEN 2 ELSE 3 END,
                                CASE t.prioridade WHEN 'critica' THEN 1 WHEN 'alta' THEN 2 WHEN 'media' THEN 3 ELSE 4 END, t.id""")
        tarefas = [dict(t) for t in cur.fetchall()]
        cur.execute("SELECT id, titulo FROM goals ORDER BY id")
        metas = [dict(g) for g in cur.fetchall()]
        cur.close()
        close_conn(conn)

        pendentes = [t for t in tarefas if t["status"] != "concluida"]
        concluidas = [t for t in tarefas if t["status"] == "concluida"]

        def render_tarefa(t):
            prio = t.get("prioridade") or "media"
            cls = "critica" if prio == "critica" else ("alta" if prio == "alta" else "")
            if t["status"] == "concluida":
                cls += " concluida"
            gtxt = f'<p>Meta: {t["goal_titulo"]}</p>' if t.get("goal_titulo") else ""
            botoes = ""
            if t["status"] == "concluida":
                botoes = f'<form method="POST" action="/plano/tarefa/{t["id"]}/reabrir" style="display:inline;"><button class="btn btn-cinza" type="submit">REABRIR</button></form>'
            else:
                botoes = f'<form method="POST" action="/plano/tarefa/{t["id"]}/concluir" style="display:inline;"><button class="btn btn-verde" type="submit">CONCLUIR</button></form>'
            botoes += f'<form method="POST" action="/plano/tarefa/{t["id"]}/excluir" onsubmit="return confirm(\'Excluir?\');" style="display:inline;"><button class="btn btn-vermelho" type="submit">EXCLUIR</button></form>'
            return f"""
            <div class="tarefa {cls}">
                <h2>{t["titulo"]}</h2>
                {f'<p>{t["descricao"]}</p>' if t.get("descricao") else ""}
                {gtxt}
                <p>Prioridade: {prio} · Status: {t["status"]}</p>
                {botoes}
            </div>"""

        lista_pend = "".join(render_tarefa(t) for t in pendentes)
        lista_conc = "".join(render_tarefa(t) for t in concluidas)

        metas_opts = "".join(f'<option value="{m["id"]}">{m["titulo"]}</option>' for m in metas)

        form_nova = f"""
        <details><summary>+ CRIAR NOVA TAREFA</summary>
            <div class="form-box">
                <form method="POST" action="/plano/tarefa/criar">
                    <label>Titulo *</label><input type="text" name="titulo" required>
                    <label>Descricao</label><textarea name="descricao" rows="2"></textarea>
                    <label>Meta (opcional)</label><select name="goal_id"><option value="">Sem meta</option>{metas_opts}</select>
                    <label>Prioridade</label><select name="prioridade">
                        <option value="critica">Critica</option><option value="alta">Alta</option>
                        <option value="media" selected>Media</option><option value="baixa">Baixa</option>
                    </select>
                    <button class="btn btn-verde" type="submit">CRIAR</button>
                </form>
            </div>
        </details>"""

        corpo = f"""
        {_topo("tarefas")}
        <div class="container">
            {form_nova}
            <h2 style="color:#ff5555;font-size:14px;">PENDENTES ({len(pendentes)})</h2>
            {lista_pend if lista_pend else '<p class="texto-cinza">Nada pendente.</p>'}
            <h2 style="color:#00d97e;font-size:14px;margin-top:20px;">CONCLUIDAS ({len(concluidas)})</h2>
            {lista_conc if lista_conc else '<p class="texto-cinza">Nenhuma concluida ainda.</p>'}
        </div>"""
        return HTMLResponse(_html("Tarefas", corpo))

    # ============================================================
    # BLOQUEIOS
    # ============================================================
    @app.get("/plano/bloqueios", response_class=HTMLResponse)
    def plano_bloqueios(request: Request, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM blockers ORDER BY CASE status WHEN 'aberto' THEN 1 ELSE 2 END, prioridade, id DESC")
        bs = [dict(b) for b in cur.fetchall()]
        cur.close()
        close_conn(conn)

        html_b = ""
        for b in bs:
            badge = "b-vermelho" if b["status"] == "aberto" else "b-verde"
            html_b += f"""
            <div class="bloco" style="border-left:3px solid {'#ff5555' if b["status"]=='aberto' else '#00d97e'};">
                <h2>{b["titulo"]} <span class="badge {badge}" style="float:right;">{b["status"]}</span></h2>
                <p class="texto-cinza">Problema: {b.get("problema") or ""}</p>
                <p class="texto-cinza">Impacto: {b.get("impacto") or ""}</p>
                <p class="texto-cinza">Solucao: {b.get("solucao_necessaria") or ""}</p>
                {"<form method='POST' action='/plano/bloqueio/" + str(b["id"]) + "/resolver' style='margin-top:8px;'><button class='btn btn-verde' type='submit'>RESOLVER</button></form>" if b["status"]=="aberto" else ""}
            </div>"""

        form_novo = """
        <details><summary>+ CRIAR BLOQUEIO</summary>
            <div class="form-box">
                <form method="POST" action="/plano/bloqueio/criar">
                    <label>Titulo *</label><input type="text" name="titulo" required>
                    <label>Problema</label><textarea name="problema" rows="2"></textarea>
                    <label>Impacto</label><input type="text" name="impacto">
                    <label>Solucao necessaria</label><textarea name="solucao_necessaria" rows="2"></textarea>
                    <label>Prioridade</label><select name="prioridade">
                        <option value="critica">Critica</option><option value="alta" selected>Alta</option>
                        <option value="media">Media</option>
                    </select>
                    <button class="btn btn-verde" type="submit">CRIAR</button>
                </form>
            </div>
        </details>"""

        corpo = f'{_topo("bloqueios")}<div class="container">{form_novo}{html_b if html_b else "<p class=texto-cinza>Nenhum bloqueio.</p>"}</div>'
        return HTMLResponse(_html("Bloqueios", corpo))

    # ============================================================
    # DIARIO
    # ============================================================
    @app.get("/plano/diario", response_class=HTMLResponse)
    def plano_diario(request: Request, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None), ok: str = None):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM journal_entries ORDER BY data DESC, id DESC LIMIT 100")
        entradas = [dict(e) for e in cur.fetchall()]
        cur.close()
        close_conn(conn)

        html_e = ""
        for e in entradas:
            html_e += f"""
            <div class="diario-item">
                <div class="data">{e["data"]} · {e.get("categoria") or ""}</div>
                <h3>{e["titulo"]}</h3>
                {f'<p>{e["conteudo"]}</p>' if e.get("conteudo") else ""}
                {f'<div class="res">Resultado: {e["resultado"]}</div>' if e.get("resultado") else ""}
                {f'<div class="prox">Proximo: {e["proximo_passo"]}</div>' if e.get("proximo_passo") else ""}
            </div>"""

        form_novo = """
        <details><summary>+ NOVA ENTRADA</summary>
            <div class="form-box">
                <form method="POST" action="/plano/diario/criar">
                    <label>Titulo *</label><input type="text" name="titulo" required>
                    <label>Conteudo</label><textarea name="conteudo" rows="3"></textarea>
                    <label>Categoria</label><select name="categoria">
                        <option value="">—</option><option value="produto">Produto</option>
                        <option value="comercial">Comercial</option><option value="financeiro">Financeiro</option>
                        <option value="decisao">Decisao</option><option value="problema">Problema</option>
                        <option value="conquista">Conquista</option>
                    </select>
                    <label>Resultado</label><input type="text" name="resultado">
                    <label>Proximo passo</label><input type="text" name="proximo_passo">
                    <button class="btn btn-verde" type="submit">REGISTRAR</button>
                </form>
            </div>
        </details>"""

        corpo = f'{_topo("diario")}<div class="container">{form_novo}{html_e}</div>'
        return HTMLResponse(_html("Diario", corpo))

    # ============================================================
    # SYNC
    # ============================================================
    @app.post("/plano/sync")
    def plano_sync(usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        try:
            plano_core.executar_sync(get_conn, close_conn)
        except Exception as e:
            print(f"Erro sync: {e}")
        return RedirectResponse(url="/plano?ok=sync", status_code=303)

    @app.get("/plano/sync-cron")
    def plano_sync_cron(token: str = ""):
        import os as _os
        from fastapi.responses import JSONResponse
        esperado = _os.getenv("BACKUP_TOKEN", "")
        if not esperado or token != esperado:
            return JSONResponse({"erro": "token invalido"}, status_code=403)
        try:
            r = plano_core.executar_sync(get_conn, close_conn)
            return {"status": "ok", "msg": r["mensagem"]}
        except Exception as e:
            return {"status": "erro", "msg": str(e)}

    # ============================================================
    # EDICAO — TAREFAS
    # ============================================================
    @app.post("/plano/tarefa/{tid}/concluir")
    def t_concluir(tid: int, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn(); cur = conn.cursor()
        cur.execute("UPDATE tasks SET status='concluida', concluida_em=NOW(), atualizado_em=NOW() WHERE id=%s", (tid,))
        conn.commit(); cur.close(); close_conn(conn)
        return RedirectResponse(url="/plano/tarefas", status_code=303)

    @app.post("/plano/tarefa/{tid}/reabrir")
    def t_reabrir(tid: int, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn(); cur = conn.cursor()
        cur.execute("UPDATE tasks SET status='pendente', concluida_em=NULL, atualizado_em=NOW() WHERE id=%s", (tid,))
        conn.commit(); cur.close(); close_conn(conn)
        return RedirectResponse(url="/plano/tarefas", status_code=303)

    @app.post("/plano/tarefa/{tid}/excluir")
    def t_excluir(tid: int, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn(); cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id=%s", (tid,))
        conn.commit(); cur.close(); close_conn(conn)
        return RedirectResponse(url="/plano/tarefas", status_code=303)

    @app.post("/plano/tarefa/criar")
    def t_criar(titulo: str = Form(...), descricao: str = Form(""), goal_id: str = Form(""),
                prioridade: str = Form("media"), usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        gid = int(goal_id) if goal_id and goal_id.isdigit() else None
        conn = get_conn(); cur = conn.cursor()
        cur.execute("""INSERT INTO tasks (titulo, descricao, goal_id, status, prioridade)
            VALUES (%s, %s, %s, 'pendente', %s)""", (titulo, descricao, gid, prioridade))
        conn.commit(); cur.close(); close_conn(conn)
        return RedirectResponse(url="/plano/tarefas", status_code=303)

    # ============================================================
    # EDICAO — METAS / FASES / DIARIO / BLOQUEIOS
    # ============================================================
    @app.post("/plano/meta/{mid}/atualizar")
    def m_atualizar(mid: int, valor_atual: str = Form(...), status: str = Form(""),
                    usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        try:
            v = float(valor_atual.replace(",", "."))
        except Exception:
            return RedirectResponse(url="/plano/metas", status_code=303)
        conn = get_conn(); cur = conn.cursor()
        if status:
            cur.execute("UPDATE goals SET valor_atual=%s, status=%s, atualizado_em=NOW() WHERE id=%s", (v, status, mid))
        else:
            cur.execute("UPDATE goals SET valor_atual=%s, atualizado_em=NOW() WHERE id=%s", (v, mid))
        conn.commit(); cur.close(); close_conn(conn)
        return RedirectResponse(url="/plano/metas", status_code=303)

    @app.post("/plano/fase/{fid}/atualizar")
    def f_atualizar(fid: int, status: str = Form(...), percentual: str = Form("0"),
                    usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        try:
            p = max(0, min(100, int(percentual)))
        except Exception:
            p = 0
        conn = get_conn(); cur = conn.cursor()
        cur.execute("UPDATE roadmap_phases SET status=%s, percentual=%s, atualizado_em=NOW() WHERE id=%s", (status, p, fid))
        conn.commit(); cur.close(); close_conn(conn)
        return RedirectResponse(url="/plano/fases", status_code=303)

    @app.post("/plano/diario/criar")
    def d_criar(titulo: str = Form(...), conteudo: str = Form(""), categoria: str = Form(""),
                resultado: str = Form(""), proximo_passo: str = Form(""),
                usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn(); cur = conn.cursor()
        cur.execute("""INSERT INTO journal_entries (titulo, conteudo, categoria, resultado, proximo_passo)
            VALUES (%s, %s, %s, %s, %s)""", (titulo, conteudo, categoria, resultado, proximo_passo))
        conn.commit(); cur.close(); close_conn(conn)
        return RedirectResponse(url="/plano/diario", status_code=303)

    @app.post("/plano/bloqueio/criar")
    def b_criar(titulo: str = Form(...), problema: str = Form(""), impacto: str = Form(""),
                solucao_necessaria: str = Form(""), prioridade: str = Form("alta"),
                usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn(); cur = conn.cursor()
        cur.execute("""INSERT INTO blockers (titulo, problema, impacto, solucao_necessaria, prioridade)
            VALUES (%s, %s, %s, %s, %s)""", (titulo, problema, impacto, solucao_necessaria, prioridade))
        conn.commit(); cur.close(); close_conn(conn)
        return RedirectResponse(url="/plano/bloqueios", status_code=303)

    @app.post("/plano/bloqueio/{bid}/resolver")
    def b_resolver(bid: int, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn(); cur = conn.cursor()
        cur.execute("UPDATE blockers SET status='resolvido', resolvido_em=NOW() WHERE id=%s", (bid,))
        conn.commit(); cur.close(); close_conn(conn)
        return RedirectResponse(url="/plano/bloqueios", status_code=303)