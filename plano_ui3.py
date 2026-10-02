# plano_ui3.py
# M.A Tech — Comercial, Gestao, Relatorios, Laboratorio

from fastapi import Form
from fastapi.responses import RedirectResponse, HTMLResponse


def registrar_rotas_plano_ui3(app, get_conn, close_conn, Cookie, Request):
    from psycopg2.extras import RealDictCursor
    from plano_ui import _auth, _topo, _html

    # ============================================================
    # COMERCIAL
    # ============================================================
    @app.get("/plano/comercial", response_class=HTMLResponse)
    def plano_comercial(request: Request, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # dados reais do CRM
        try:
            cur.execute("SELECT COUNT(*) as t FROM clientes")
            total_clientes = cur.fetchone()["t"]
        except Exception:
            total_clientes = 0

        try:
            cur.execute("SELECT COUNT(*) as t FROM leads_landing")
            total_leads = cur.fetchone()["t"]
        except Exception:
            total_leads = 0

        try:
            cur.execute("SELECT COUNT(*) as t FROM atendimentos")
            total_atend = cur.fetchone()["t"]
        except Exception:
            total_atend = 0

        try:
            cur.execute("SELECT status, COUNT(*) as q FROM clientes GROUP BY status")
            por_status = {r["status"]: r["q"] for r in cur.fetchall()}
        except Exception:
            por_status = {}

        # metas comerciais (viram "demonstracoes", "contatos" etc)
        cur.execute("SELECT id, titulo, valor_atual, valor_meta, unidade, status FROM goals ORDER BY id LIMIT 5")
        metas_com = [dict(g) for g in cur.fetchall()]
        cur.close()
        close_conn(conn)

        funil = ""
        for status, qtd in sorted(por_status.items(), key=lambda x: -x[1]):
            funil += f"""
            <div class="bloco" style="padding:10px 14px;">
                <div style="display:flex;justify-content:space-between;">
                    <span style="color:#e8e8e8;font-size:13px;">{status}</span>
                    <span style="color:#00d97e;font-family:monospace;font-weight:700;">{qtd}</span>
                </div>
            </div>"""

        metas_html = ""
        for m in metas_com:
            try:
                va = float(m["valor_atual"] or 0); vm = float(m["valor_meta"] or 1)
                pct = int((va/vm)*100) if vm else 0
            except Exception:
                pct = 0
            metas_html += f"""
            <div class="bloco">
                <h2 style="font-size:14px;">{m["titulo"]}</h2>
                <div style="font-family:monospace;color:#00d97e;font-size:13px;">{m["valor_atual"]:.0f} / {m["valor_meta"]:.0f} {m.get("unidade") or ""}</div>
                <div class="barra"><div class="barra-p" style="width:{pct}%;"></div></div>
            </div>"""

        corpo = f"""
        {_topo("comercial")}
        <div class="container">
            <div class="cards">
                <div class="card"><h3>Leads Landing</h3><div class="v">{total_leads}</div></div>
                <div class="card"><h3>Clientes no CRM</h3><div class="v">{total_clientes}</div></div>
                <div class="card"><h3>Atendimentos IA</h3><div class="v">{total_atend}</div></div>
            </div>
            <h2 style="font-size:14px;color:#8a8a8a;">FUNIL DE VENDAS</h2>
            {funil if funil else '<p class="texto-cinza">Sem clientes cadastrados ainda.</p>'}
            <h2 style="font-size:14px;color:#8a8a8a;margin-top:20px;">METAS COMERCIAIS</h2>
            {metas_html}
        </div>"""
        return HTMLResponse(_html("Comercial", corpo))

    # ============================================================
    # GESTAO (M.A Tech Cuida)
    # ============================================================
    @app.get("/plano/gestao", response_class=HTMLResponse)
    def plano_gestao(request: Request, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # projetos tipo cliente (gestao)
        try:
            cur.execute("SELECT * FROM projects WHERE tipo='cliente' OR tipo='consultoria' ORDER BY id DESC")
            projetos = [dict(p) for p in cur.fetchall()]
        except Exception:
            projetos = []

        try:
            cur.execute("SELECT COUNT(*) as t FROM plan_modules WHERE ativo=TRUE")
            modulos_ativos = cur.fetchone()["t"]
        except Exception:
            modulos_ativos = 0

        try:
            cur.execute("SELECT COALESCE(SUM(valor),0) as t FROM revenue_records WHERE tipo='gestao'")
            receita_gestao = float(cur.fetchone()["t"] or 0)
        except Exception:
            receita_gestao = 0.0

        cur.close()
        close_conn(conn)

        projetos_html = ""
        for p in projetos:
            projetos_html += f"""
            <div class="bloco" style="border-left:3px solid #a855f7;">
                <h2 style="font-size:14px;">{p["nome"]} <span class="badge b-cinza" style="float:right;">{p["status"]}</span></h2>
                <p class="texto-cinza">{p.get("descricao") or ""}</p>
            </div>"""

        form = """
        <details><summary>+ NOVA EMPRESA SOB GESTAO</summary>
            <div class="form-box">
                <form method="POST" action="/plano/gestao/criar">
                    <label>Nome da empresa *</label><input type="text" name="nome" required>
                    <label>Descricao do projeto</label><textarea name="descricao" rows="3"></textarea>
                    <label>Tipo</label><select name="tipo">
                        <option value="cliente">Gestao completa</option>
                        <option value="consultoria">Consultoria</option>
                    </select>
                    <button class="btn btn-verde" type="submit">CRIAR</button>
                </form>
            </div>
        </details>"""

        corpo = f"""
        {_topo("gestao")}
        <div class="container">
            <div class="bloco" style="background:linear-gradient(135deg,#141414,#1a0f2a);border-left:3px solid #a855f7;">
                <h2 style="color:#c084fc;">M.A TECH CUIDA</h2>
                <p class="texto-cinza">A empresa identifica o problema, estrutura o processo, implementa a tecnologia e acompanha a gestao.</p>
            </div>
            <div class="cards">
                <div class="card"><h3>Empresas sob Gestao</h3><div class="v">{len(projetos)}</div></div>
                <div class="card"><h3>Modulos Ativos</h3><div class="v">{modulos_ativos}</div></div>
                <div class="card"><h3>Receita de Gestao</h3><div class="v">R$ {receita_gestao:.2f}</div></div>
            </div>
            {form}
            <h2 style="font-size:14px;color:#8a8a8a;">EMPRESAS ATENDIDAS</h2>
            {projetos_html if projetos_html else '<p class="texto-cinza">Nenhuma empresa sob gestao ainda.</p>'}
        </div>"""
        return HTMLResponse(_html("Gestao", corpo))

    @app.post("/plano/gestao/criar")
    def gestao_criar(nome: str = Form(...), descricao: str = Form(""), tipo: str = Form("cliente"),
                     usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn(); cur = conn.cursor()
        cur.execute("INSERT INTO projects (nome, descricao, tipo, status) VALUES (%s, %s, %s, 'em_execucao')",
                    (nome, descricao, tipo))
        conn.commit(); cur.close(); close_conn(conn)
        return RedirectResponse(url="/plano/gestao", status_code=303)

    # ============================================================
    # LABORATORIO DE PRODUTOS (ideias)
    # ============================================================
    @app.get("/plano/lab", response_class=HTMLResponse)
    def plano_lab(request: Request, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM products WHERE status IN ('ideia','pesquisa','validacao') ORDER BY id DESC")
        ideias = [dict(p) for p in cur.fetchall()]
        cur.close()
        close_conn(conn)

        html_i = ""
        for p in ideias:
            ico = {"ideia":"lampada","pesquisa":"lupa","validacao":"teste"}.get(p["status"],"")
            html_i += f"""
            <div class="bloco" style="border-left:3px solid #f5c542;">
                <h2 style="font-size:14px;">{p["nome"]} <span class="badge b-amarelo" style="float:right;">{p["status"]}</span></h2>
                <p class="texto-cinza">{p.get("descricao") or ""}</p>
            </div>"""

        form = """
        <details><summary>+ NOVA IDEIA</summary>
            <div class="form-box">
                <form method="POST" action="/plano/lab/criar">
                    <label>Nome da ideia *</label><input type="text" name="nome" required>
                    <label>Problema que resolve</label><textarea name="problema_que_resolve" rows="2"></textarea>
                    <label>Publico</label><input type="text" name="publico">
                    <label>Solucao</label><textarea name="solucao" rows="2"></textarea>
                    <label>Status</label><select name="status">
                        <option value="ideia">Ideia</option><option value="pesquisa">Pesquisa</option>
                        <option value="validacao">Validacao</option>
                    </select>
                    <button class="btn btn-verde" type="submit">CRIAR</button>
                </form>
            </div>
        </details>"""

        corpo = f"""
        {_topo("lab")}
        <div class="container">
            <div class="bloco" style="background:linear-gradient(135deg,#141414,#1f1a0a);border-left:3px solid #f5c542;">
                <h2 style="color:#f5c542;">LABORATORIO DE PRODUTOS</h2>
                <p class="texto-cinza">Ideias futuras da M.A Tech. Cadastre aqui antes de decidir se vale construir.</p>
            </div>
            {form}
            {html_i if html_i else '<p class="texto-cinza">Nenhuma ideia cadastrada.</p>'}
        </div>"""
        return HTMLResponse(_html("Laboratorio", corpo))

    @app.post("/plano/lab/criar")
    def lab_criar(nome: str = Form(...), problema_que_resolve: str = Form(""), publico: str = Form(""),
                  solucao: str = Form(""), status: str = Form("ideia"),
                  usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn(); cur = conn.cursor()
        cur.execute("""INSERT INTO products (nome, problema_que_resolve, publico, solucao, status)
            VALUES (%s, %s, %s, %s, %s)""", (nome, problema_que_resolve, publico, solucao, status))
        conn.commit(); cur.close(); close_conn(conn)
        return RedirectResponse(url="/plano/lab", status_code=303)

    # ============================================================
    # RELATORIOS
    # ============================================================
    @app.get("/plano/relatorios", response_class=HTMLResponse)
    def plano_relatorios(request: Request, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # dados para o relatorio semanal
        try:
            cur.execute("""SELECT t.titulo, t.status, t.prioridade FROM tasks t
                           WHERE t.atualizado_em >= NOW() - INTERVAL '7 days'
                           ORDER BY t.status, t.prioridade LIMIT 30""")
            tarefas_semana = [dict(t) for t in cur.fetchall()]
        except Exception:
            tarefas_semana = []

        # dados para o relatorio mensal
        try:
            cur.execute("""SELECT COALESCE(SUM(valor),0) as receita FROM pagamentos
                           WHERE status='pago' AND criado_em >= DATE_TRUNC('month', CURRENT_DATE)""")
            receita_mes = float(cur.fetchone()["receita"] or 0)
        except Exception:
            receita_mes = 0.0

        try:
            cur.execute("SELECT COUNT(*) as t FROM vendedores WHERE plano != 'gratis'")
            clientes_pagantes = cur.fetchone()["t"]
        except Exception:
            clientes_pagantes = 0

        try:
            cur.execute("""SELECT COUNT(*) as t FROM tasks
                           WHERE status='concluida' AND concluida_em >= DATE_TRUNC('month', CURRENT_DATE)""")
            tarefas_mes = cur.fetchone()["t"]
        except Exception:
            tarefas_mes = 0

        cur.close()
        close_conn(conn)

        sem_conc = [t for t in tarefas_semana if t["status"] == "concluida"]
        sem_pend = [t for t in tarefas_semana if t["status"] != "concluida"]

        sem_html = ""
        for t in sem_conc[:10]:
            sem_html += f'<div class="bloco" style="padding:8px 12px;border-left:3px solid #00d97e;"><span style="color:#00d97e;font-size:13px;">OK</span> {t["titulo"]}</div>'
        for t in sem_pend[:10]:
            sem_html += f'<div class="bloco" style="padding:8px 12px;border-left:3px solid #f5c542;"><span style="color:#f5c542;font-size:13px;">pendente</span> {t["titulo"]}</div>'

        corpo = f"""
        {_topo("relatorios")}
        <div class="container">
            <div class="bloco">
                <h2>RELATORIO DA SEMANA</h2>
                <p class="texto-cinza">Ultimos 7 dias</p>
                <div class="cards" style="margin-top:10px;">
                    <div class="card"><h3>Tarefas concluidas</h3><div class="v">{len(sem_conc)}</div></div>
                    <div class="card"><h3>Em andamento</h3><div class="v">{len(sem_pend)}</div></div>
                </div>
                {sem_html if sem_html else '<p class="texto-cinza">Nada aconteceu nessa semana.</p>'}
            </div>
            <div class="bloco">
                <h2>RELATORIO DO MES</h2>
                <p class="texto-cinza">Mes atual</p>
                <div class="cards" style="margin-top:10px;">
                    <div class="card"><h3>Receita do mes</h3><div class="v">R$ {receita_mes:.2f}</div></div>
                    <div class="card"><h3>Clientes pagantes</h3><div class="v">{clientes_pagantes}</div></div>
                    <div class="card"><h3>Tarefas concluidas</h3><div class="v">{tarefas_mes}</div></div>
                </div>
            </div>
        </div>"""
        return HTMLResponse(_html("Relatorios", corpo))