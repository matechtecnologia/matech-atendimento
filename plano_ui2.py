# plano_ui2.py
# M.A Tech — Telas adicionais do painel
# Produtos, Projetos, Decisoes, Financeiro

from fastapi import Form
from fastapi.responses import RedirectResponse, HTMLResponse


def registrar_rotas_plano_ui2(app, get_conn, close_conn, Cookie, Request):
    from psycopg2.extras import RealDictCursor
    from plano_ui import _auth, _topo, _html

    # ============================================================
    # PRODUTOS
    # ============================================================
    @app.get("/plano/produtos", response_class=HTMLResponse)
    def plano_produtos(request: Request, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM products ORDER BY id")
        ps = [dict(p) for p in cur.fetchall()]
        cur.close()
        close_conn(conn)

        html_p = ""
        for p in ps:
            badge = "b-verde" if p["status"] == "producao" else ("b-amarelo" if p["status"] == "desenvolvimento" else "b-cinza")
            html_p += f"""
            <div class="bloco" style="border-left:3px solid {'#00d97e' if p['status']=='producao' else '#5a5a5a'};">
                <h2>{p['nome']} <span class="badge {badge}" style="float:right;">{p['status']}</span></h2>
                <p class="texto-cinza">{p.get('descricao') or ''}</p>
                <p class="texto-cinza">Prioridade: {p.get('prioridade') or '-'}</p>
            </div>"""

        form = """
        <details><summary>+ NOVO PRODUTO</summary>
            <div class="form-box">
                <form method="POST" action="/plano/produto/criar">
                    <label>Nome *</label><input type="text" name="nome" required>
                    <label>Descricao</label><textarea name="descricao" rows="3"></textarea>
                    <label>Status</label><select name="status">
                        <option value="ideia">Ideia</option><option value="pesquisa">Pesquisa</option>
                        <option value="validacao">Validacao</option><option value="desenvolvimento">Desenvolvimento</option>
                        <option value="producao">Producao</option><option value="monetizacao">Monetizacao</option>
                        <option value="pausado">Pausado</option><option value="descartado">Descartado</option>
                    </select>
                    <label>Prioridade</label><select name="prioridade">
                        <option value="critica">Critica</option><option value="alta">Alta</option>
                        <option value="media" selected>Media</option><option value="baixa">Baixa</option>
                    </select>
                    <button class="btn btn-verde" type="submit">CRIAR</button>
                </form>
            </div>
        </details>"""

        corpo = f'{_topo("produtos")}<div class="container">{form}{html_p}</div>'
        return HTMLResponse(_html("Produtos", corpo))

    @app.post("/plano/produto/criar")
    def produto_criar(nome: str = Form(...), descricao: str = Form(""), status: str = Form("ideia"),
                      prioridade: str = Form("media"), usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn(); cur = conn.cursor()
        cur.execute("INSERT INTO products (nome, descricao, status, prioridade) VALUES (%s, %s, %s, %s)",
                    (nome, descricao, status, prioridade))
        conn.commit(); cur.close(); close_conn(conn)
        return RedirectResponse(url="/plano/produtos", status_code=303)

    # ============================================================
    # PROJETOS
    # ============================================================
    @app.get("/plano/projetos", response_class=HTMLResponse)
    def plano_projetos(request: Request, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM projects ORDER BY id")
        ps = [dict(p) for p in cur.fetchall()]
        cur.close()
        close_conn(conn)

        html_p = ""
        for p in ps:
            badge = "b-verde" if p["status"] == "concluido" else ("b-amarelo" if p["status"] == "em_execucao" else "b-cinza")
            html_p += f"""
            <div class="bloco">
                <h2>{p['nome']} <span class="badge {badge}" style="float:right;">{p['status']}</span></h2>
                <p class="texto-cinza">{p.get('descricao') or ''}</p>
                <div class="barra"><div class="barra-p" style="width:{p.get('percentual') or 0}%;"></div></div>
            </div>"""

        form = """
        <details><summary>+ NOVO PROJETO</summary>
            <div class="form-box">
                <form method="POST" action="/plano/projeto/criar">
                    <label>Nome *</label><input type="text" name="nome" required>
                    <label>Descricao</label><textarea name="descricao" rows="3"></textarea>
                    <label>Tipo</label><select name="tipo">
                        <option value="produto">Produto</option><option value="cliente">Cliente</option>
                        <option value="interno">Interno</option><option value="consultoria">Consultoria</option>
                    </select>
                    <button class="btn btn-verde" type="submit">CRIAR</button>
                </form>
            </div>
        </details>"""

        corpo = f'{_topo("projetos")}<div class="container">{form}{html_p if html_p else "<p class=texto-cinza>Nenhum projeto.</p>"}</div>'
        return HTMLResponse(_html("Projetos", corpo))

    @app.post("/plano/projeto/criar")
    def projeto_criar(nome: str = Form(...), descricao: str = Form(""), tipo: str = Form("produto"),
                      usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn(); cur = conn.cursor()
        cur.execute("INSERT INTO projects (nome, descricao, tipo) VALUES (%s, %s, %s)", (nome, descricao, tipo))
        conn.commit(); cur.close(); close_conn(conn)
        return RedirectResponse(url="/plano/projetos", status_code=303)

    # ============================================================
    # DECISOES
    # ============================================================
    @app.get("/plano/decisoes", response_class=HTMLResponse)
    def plano_decisoes(request: Request, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM decisions ORDER BY id DESC LIMIT 100")
        ds = [dict(d) for d in cur.fetchall()]
        cur.close()
        close_conn(conn)

        html_d = ""
        for d in ds:
            html_d += f"""
            <div class="bloco" style="border-left:3px solid #a855f7;">
                <div class="data" style="color:#5a5a5a;font-size:11px;font-family:monospace;">{d.get('data_decisao') or ''}</div>
                <h2>{d['titulo']}</h2>
                <p style="font-size:14px;color:#e8e8e8;">{d['decisao']}</p>
                {f'<p class="texto-cinza">Motivo: {d["motivo"]}</p>' if d.get('motivo') else ''}
                {f'<p class="texto-cinza">Resultado: {d["resultado_real"]}</p>' if d.get('resultado_real') else ''}
            </div>"""

        form = """
        <details><summary>+ NOVA DECISAO</summary>
            <div class="form-box">
                <form method="POST" action="/plano/decisao/criar">
                    <label>Titulo *</label><input type="text" name="titulo" required>
                    <label>Decisao *</label><textarea name="decisao" rows="3" required></textarea>
                    <label>Motivo</label><textarea name="motivo" rows="2"></textarea>
                    <label>Alternativas consideradas</label><textarea name="alternativas" rows="2"></textarea>
                    <label>Impacto esperado</label><input type="text" name="impacto_esperado">
                    <button class="btn btn-verde" type="submit">REGISTRAR</button>
                </form>
            </div>
        </details>"""

        corpo = f'{_topo("decisoes")}<div class="container">{form}{html_d if html_d else "<p class=texto-cinza>Nenhuma decisao registrada.</p>"}</div>'
        return HTMLResponse(_html("Decisoes", corpo))

    @app.post("/plano/decisao/criar")
    def decisao_criar(titulo: str = Form(...), decisao: str = Form(...), motivo: str = Form(""),
                      alternativas: str = Form(""), impacto_esperado: str = Form(""),
                      usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn(); cur = conn.cursor()
        cur.execute("""INSERT INTO decisions (titulo, decisao, motivo, alternativas, impacto_esperado)
            VALUES (%s, %s, %s, %s, %s)""", (titulo, decisao, motivo, alternativas, impacto_esperado))
        conn.commit(); cur.close(); close_conn(conn)
        return RedirectResponse(url="/plano/decisoes", status_code=303)

    # ============================================================
    # FINANCEIRO
    # ============================================================
    @app.get("/plano/financeiro", response_class=HTMLResponse)
    def plano_financeiro(request: Request, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT COALESCE(SUM(valor),0) as t FROM pagamentos WHERE status='pago'")
        receita_total = float(cur.fetchone()["t"] or 0)

        cur.execute("""SELECT COALESCE(SUM(valor),0) as t FROM pagamentos
                       WHERE status='pago' AND criado_em >= DATE_TRUNC('month', CURRENT_DATE)""")
        mrr = float(cur.fetchone()["t"] or 0)

        cur.execute("SELECT COUNT(*) as t FROM vendedores WHERE plano != 'gratis'")
        clientes_pagantes = cur.fetchone()["t"]

        cur.execute("SELECT * FROM revenue_records ORDER BY data DESC, id DESC LIMIT 50")
        recs = [dict(r) for r in cur.fetchall()]
        cur.close()
        close_conn(conn)

        html_r = ""
        for r in recs:
            html_r += f"""
            <div class="bloco" style="padding:10px 14px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <div style="font-size:13px;color:#e8e8e8;">{r['descricao'] or r['tipo'] or 'Receita'}</div>
                        <div class="texto-cinza" style="font-size:11px;">{r['data']} · {r.get('cliente') or ''}</div>
                    </div>
                    <div style="color:#00d97e;font-family:monospace;font-weight:700;">R$ {float(r['valor']):.2f}</div>
                </div>
            </div>"""

        form = """
        <details><summary>+ REGISTRAR RECEITA</summary>
            <div class="form-box">
                <form method="POST" action="/plano/receita/criar">
                    <label>Descricao *</label><input type="text" name="descricao" required>
                    <label>Valor *</label><input type="text" name="valor" required placeholder="97.00">
                    <label>Tipo</label><select name="tipo">
                        <option value="software">Software</option><option value="gestao">Gestao</option>
                        <option value="consultoria">Consultoria</option><option value="implantacao">Implantacao</option>
                    </select>
                    <label>Cliente</label><input type="text" name="cliente">
                    <button class="btn btn-verde" type="submit">REGISTRAR</button>
                </form>
            </div>
        </details>"""

        corpo = f"""
        {_topo("financeiro")}
        <div class="container">
            <div class="cards">
                <div class="card"><h3>Receita Total</h3><div class="v">R$ {receita_total:.2f}</div></div>
                <div class="card"><h3>MRR (mes)</h3><div class="v">R$ {mrr:.2f}</div></div>
                <div class="card"><h3>Clientes Pagantes</h3><div class="v">{clientes_pagantes}</div></div>
            </div>
            {form}
            <h2 style="font-size:14px;color:#8a8a8a;">ULTIMAS RECEITAS</h2>
            {html_r if html_r else '<p class="texto-cinza">Nenhuma receita registrada.</p>'}
        </div>"""
        return HTMLResponse(_html("Financeiro", corpo))

    @app.post("/plano/receita/criar")
    def receita_criar(descricao: str = Form(...), valor: str = Form(...), tipo: str = Form("software"),
                      cliente: str = Form(""), usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        try:
            v = float(valor.replace(",", "."))
        except Exception:
            return RedirectResponse(url="/plano/financeiro", status_code=303)
        conn = get_conn(); cur = conn.cursor()
        cur.execute("INSERT INTO revenue_records (descricao, valor, tipo, cliente) VALUES (%s, %s, %s, %s)",
                    (descricao, v, tipo, cliente))
        conn.commit(); cur.close(); close_conn(conn)
        return RedirectResponse(url="/plano/financeiro", status_code=303)