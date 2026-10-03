# plano_roi.py
# M.A Tech — Tela de ROI real (Receita x Custos)
# Criado em: 03/10/2026

from fastapi import Form
from fastapi.responses import RedirectResponse, HTMLResponse


def registrar_rotas_roi(app, get_conn, close_conn, Cookie, Request):
    from psycopg2.extras import RealDictCursor
    from plano_ui import _auth, _topo, _html

    def _mes_ano():
        from datetime import datetime as _dt
        return _dt.now().strftime("%Y-%m")

    def _garantir_tabela():
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS custos_mensais (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            categoria TEXT,
            valor NUMERIC NOT NULL,
            mes_ano TEXT NOT NULL,
            observacao TEXT,
            criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )""")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_custos_mes ON custos_mensais(mes_ano)")
        conn.commit()
        cur.close()
        close_conn(conn)

    try:
        _garantir_tabela()
        print("Plano ROI: tabela custos_mensais OK")
    except Exception as e:
        print(f"Plano ROI erro tabela: {e}")

    @app.get("/plano/roi", response_class=HTMLResponse)
    def plano_roi(request: Request, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None), mes: str = None, ok: str = None):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")

        mes_ref = mes or _mes_ano()

        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Receita do mes (pagamentos pagos)
        cur.execute("""
            SELECT COALESCE(SUM(valor), 0) as total
            FROM pagamentos
            WHERE status = 'pago'
              AND TO_CHAR(criado_em, 'YYYY-MM') = %s
        """, (mes_ref,))
        receita = float(cur.fetchone()["total"] or 0)

        # Receita total (todos os tempos)
        cur.execute("SELECT COALESCE(SUM(valor), 0) as total FROM pagamentos WHERE status = 'pago'")
        receita_total = float(cur.fetchone()["total"] or 0)

        # Clientes pagantes ativos
        cur.execute("SELECT COUNT(*) as t FROM vendedores WHERE plano != 'gratis'")
        clientes_pagos = cur.fetchone()["t"]

        # Respostas IA do mes
        cur.execute("SELECT COALESCE(total, 0) as t FROM respostas_ia WHERE mes_ano = %s", (mes_ref,))
        r = cur.fetchone()
        respostas_mes = r["t"] if r else 0

        # Custos do mes
        cur.execute("""SELECT id, nome, categoria, valor, observacao, criado_em
                       FROM custos_mensais WHERE mes_ano = %s ORDER BY id""", (mes_ref,))
        custos_lista = [dict(c) for c in cur.fetchall()]
        custos_total = sum(float(c["valor"]) for c in custos_lista)

        cur.close()
        close_conn(conn)

        # Estimativa de custo IA: R$ 0,008 por resposta (Groq)
        custo_ia_estimado = respostas_mes * 0.008
        custos_total_com_ia = custos_total + custo_ia_estimado

        lucro = receita - custos_total_com_ia
        roi = ((lucro / custos_total_com_ia) * 100) if custos_total_com_ia > 0 else 0
        margem = ((lucro / receita) * 100) if receita > 0 else 0

        # Cores por resultado
        roi_cor = "#00d97e" if roi >= 100 else ("#f5c542" if roi >= 0 else "#ff5555")

        custos_html = ""
        for c in custos_lista:
            custos_html += f"""
            <div class="bloco" style="padding:10px 14px;display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="color:#e8e8e8;font-size:14px;">{c['nome']}</div>
                    <div class="texto-cinza" style="font-size:11px;">{c.get('categoria') or 'sem categoria'}</div>
                </div>
                <div style="display:flex;align-items:center;gap:12px;">
                    <span style="color:#ff5555;font-family:monospace;font-weight:700;">- R$ {float(c['valor']):.2f}</span>
                    <form method="POST" action="/plano/roi/custo/{c['id']}/excluir" style="margin:0;">
                        <button type="submit" class="btn btn-vermelho" style="padding:4px 10px;font-size:11px;" onclick="return confirm('Excluir?');">X</button>
                    </form>
                </div>
            </div>"""

        form = f"""
        <details><summary>+ ADICIONAR CUSTO DO MES ({mes_ref})</summary>
            <div class="form-box">
                <form method="POST" action="/plano/roi/custo/criar">
                    <input type="hidden" name="mes_ano" value="{mes_ref}">
                    <label>Nome do custo *</label>
                    <input type="text" name="nome" required placeholder="Ex: Groq IA, Render, Supabase">
                    <label>Categoria</label>
                    <select name="categoria">
                        <option value="ia">IA / API</option>
                        <option value="infra">Infraestrutura</option>
                        <option value="ferramenta">Ferramenta</option>
                        <option value="imposto">Imposto / Contador</option>
                        <option value="marketing">Marketing</option>
                        <option value="outro">Outro</option>
                    </select>
                    <label>Valor (R$) *</label>
                    <input type="text" name="valor" required placeholder="97.00">
                    <label>Observacao</label>
                    <input type="text" name="observacao">
                    <button type="submit" class="btn btn-verde">ADICIONAR</button>
                </form>
            </div>
        </details>"""

        corpo = f"""
        {_topo("financeiro")}
        <div class="container">
            {'<div class="aviso">Custo adicionado.</div>' if ok == '1' else ''}

            <div class="bloco" style="background:linear-gradient(135deg,#141414,#0f1a15);">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
                    <h2 style="margin:0;">MES: {mes_ref}</h2>
                    <form method="GET" action="/plano/roi" style="margin:0;display:flex;gap:8px;align-items:center;">
                        <input type="text" name="mes" value="{mes_ref}" placeholder="2026-10" style="background:#0a0a0a;border:1px solid #2a2a2a;color:#00d97e;padding:8px 12px;border-radius:6px;font-family:monospace;font-size:13px;width:110px;">
                        <button type="submit" class="btn btn-verde" style="padding:8px 16px;">VER</button>
                    </form>
                </div>
            </div>

            <div class="cards">
                <div class="card"><h3>Receita do mes</h3><div class="v" style="color:#00d97e;">R$ {receita:.2f}</div></div>
                <div class="card"><h3>Custos totais</h3><div class="v" style="color:#ff5555;">R$ {custos_total_com_ia:.2f}</div><div class="sub">inclui IA estimada</div></div>
                <div class="card"><h3>Lucro real</h3><div class="v" style="color:{'#00d97e' if lucro >= 0 else '#ff5555'};">R$ {lucro:.2f}</div></div>
                <div class="card"><h3>ROI</h3><div class="v" style="color:{roi_cor};">{roi:.0f}%</div><div class="sub">{'lucrando' if roi > 0 else 'prejuizo'}</div></div>
                <div class="card"><h3>Margem</h3><div class="v" style="color:#a855f7;">{margem:.0f}%</div></div>
                <div class="card"><h3>Clientes pagantes</h3><div class="v">{clientes_pagos}</div></div>
                <div class="card"><h3>Respostas IA no mes</h3><div class="v">{respostas_mes}</div></div>
                <div class="card"><h3>Custo IA estimado</h3><div class="v" style="color:#f5c542;">R$ {custo_ia_estimado:.2f}</div></div>
            </div>

            <div class="bloco" style="border-left:3px solid #a855f7;">
                <h2>COMO O ROI E CALCULADO</h2>
                <p class="texto-cinza">Lucro = Receita do mes - Custos totais (manuais + IA estimada)</p>
                <p class="texto-cinza">ROI = (Lucro / Custos) x 100</p>
                <p class="texto-cinza">Margem = (Lucro / Receita) x 100</p>
                <p class="texto-cinza" style="margin-top:8px;font-size:11px;">Custo IA estimado: R$ 0,008 por resposta (Groq gpt-oss-120b). Ajuste conforme o provedor.</p>
            </div>

            <div class="bloco" style="background:linear-gradient(135deg,#141414,#0f1a15);">
                <h2>RECEITA ACUMULADA</h2>
                <div style="font-size:28px;font-family:monospace;color:#00d97e;">R$ {receita_total:.2f}</div>
                <p class="texto-cinza">Total desde o inicio (todos os meses)</p>
            </div>

            {form}

            <h2 style="font-size:14px;color:#8a8a8a;">CUSTOS DO MES ({len(custos_lista)})</h2>
            {custos_html if custos_html else '<p class="texto-cinza">Nenhum custo cadastrado neste mes.</p>'}
        </div>"""
        return HTMLResponse(_html("ROI Real", corpo))

    @app.post("/plano/roi/custo/criar")
    def roi_custo_criar(nome: str = Form(...), categoria: str = Form("outro"), valor: str = Form(...),
                        mes_ano: str = Form(...), observacao: str = Form(""),
                        usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        try:
            v = float(valor.replace(",", "."))
        except Exception:
            return RedirectResponse(url="/plano/roi?mes=" + mes_ano, status_code=303)
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""INSERT INTO custos_mensais (nome, categoria, valor, mes_ano, observacao)
                       VALUES (%s, %s, %s, %s, %s)""", (nome, categoria, v, mes_ano, observacao))
        conn.commit()
        cur.close()
        close_conn(conn)
        return RedirectResponse(url="/plano/roi?mes=" + mes_ano + "&ok=1", status_code=303)

    @app.post("/plano/roi/custo/{custo_id}/excluir")
    def roi_custo_excluir(custo_id: int, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT mes_ano FROM custos_mensais WHERE id = %s", (custo_id,))
        r = cur.fetchone()
        mes = r[0] if r else None
        cur.execute("DELETE FROM custos_mensais WHERE id = %s", (custo_id,))
        conn.commit()
        cur.close()
        close_conn(conn)
        return RedirectResponse(url="/plano/roi" + (f"?mes={mes}" if mes else ""), status_code=303)