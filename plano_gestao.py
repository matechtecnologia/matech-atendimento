# plano_gestao.py
# Tela de gestao consolidada do Plano M.A Tech

from fastapi.responses import RedirectResponse, HTMLResponse

CSS = """
body{background:#0a0a0a;color:#e8e8e8;font-family:-apple-system,sans-serif;margin:0}
.topo{background:#0f1a15;padding:14px 20px;border-bottom:1px solid #00d97e33;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px}
.topo h1{color:#00d97e;font-size:18px;margin:0}
.menu{display:flex;gap:12px;flex-wrap:wrap}
.menu a{color:#e8e8e8;text-decoration:none;font-size:13px;padding:6px 10px;border-radius:6px}
.menu a:hover,.menu a.ativo{background:#00d97e22;color:#00d97e}
.container{max-width:1200px;margin:20px auto;padding:0 20px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin-bottom:20px}
.card{background:#141414;border:1px solid #222;border-radius:8px;padding:18px}
.card h3{color:#8a8a8a;font-size:11px;text-transform:uppercase;margin:0 0 8px 0;letter-spacing:.5px}
.card .v{color:#00d97e;font-size:28px;font-weight:700;font-family:monospace}
.card .sub{color:#5a5a5a;font-size:11px;margin-top:6px}
.bloco{background:#141414;border:1px solid #222;border-radius:8px;padding:18px;margin-bottom:14px}
.bloco h2{font-size:15px;margin:0 0 10px 0;color:#e8e8e8}
.item{background:#0a0a0a;border:1px solid #222;border-left:3px solid #00d97e;border-radius:8px;padding:12px;margin-bottom:8px}
.item.critico{border-left-color:#ff5555}
.item.alta{border-left-color:#f5c542}
.item h4{font-size:13px;margin:0 0 4px 0;color:#e8e8e8}
.item p{color:#8a8a8a;font-size:11px;margin:2px 0}
.texto-cinza{color:#8a8a8a;font-size:13px}
.badge{display:inline-block;padding:3px 8px;border-radius:10px;font-size:10px;font-weight:700;text-transform:uppercase}
.b-verde{background:#0a1f15;color:#00d97e;border:1px solid #00d97e}
.b-amarelo{background:#1f1a0a;color:#f5c542;border:1px solid #f5c542}
.b-vermelho{background:#1f0a0a;color:#ff5555;border:1px solid #ff5555}
.barra{height:8px;background:#2a2a2a;border-radius:4px;overflow:hidden;margin-top:8px}
.barra-p{height:100%;background:#00d97e}
"""

def _auth(uid,tipo): return uid and tipo=="admin"

def _topo(ativo):
    itens=[("/plano","Dashboard","d"),("/plano/fases","Roadmap","f"),("/plano/metas","Metas","m"),
           ("/plano/tarefas","Tarefas","t"),("/plano/projetos","Projetos","p"),("/plano/produtos","Produtos","pr"),
           ("/plano/bloqueios","Bloqueios","b"),("/plano/gestao","Gestao","g"),("/plano/pendencias","Pendencias","pe"),
           ("/plano/proximos","Proximos","px"),("/plano/diario","Diario","di")]
    menu="".join(f'<a href="{h}" class="{"ativo" if ativo==k else ""}">{n}</a>' for h,n,k in itens)
    return f'<div class="topo"><h1>Plano M.A Tech</h1><div class="menu">{menu}</div></div>'

def _html(t,c): return f'<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{t}</title><style>{CSS}</style></head><body>{c}</body></html>'

def registrar_rotas_gestao(app, get_conn, close_conn, Cookie, Request):
    from psycopg2.extras import RealDictCursor

    @app.get("/plano/gestao", response_class=HTMLResponse)
    def gestao(usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo): return RedirectResponse(url="/login")
        conn=get_conn(); cur=conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT COUNT(*) as t FROM tasks WHERE status='pendente'")
        pend=cur.fetchone()["t"]
        cur.execute("SELECT COUNT(*) as t FROM tasks WHERE status='concluida'")
        conc=cur.fetchone()["t"]
        cur.execute("SELECT COUNT(*) as t FROM blockers WHERE status='aberto'")
        bloq=cur.fetchone()["t"]
        cur.execute("SELECT COUNT(*) as t FROM projects WHERE status='em_andamento'")
        proj=cur.fetchone()["t"]
        cur.execute("SELECT COUNT(*) as t FROM goals WHERE status='em_andamento'")
        metas=cur.fetchone()["t"]
        cur.execute("SELECT COALESCE(SUM(valor),0) as s FROM pagamentos WHERE status='pago'")
        mrr=float(cur.fetchone()["s"] or 0)
        
        # top 5 tarefas criticas
        cur.execute("SELECT titulo, prioridade FROM tasks WHERE status='pendente' ORDER BY CASE prioridade WHEN 'critica' THEN 1 WHEN 'alta' THEN 2 ELSE 3 END LIMIT 5")
        top=cur.fetchall()
        
        # bloqueios
        cur.execute("SELECT titulo, problema FROM blockers WHERE status='aberto' ORDER BY prioridade LIMIT 5")
        bl=cur.fetchall()
        
        cur.close(); close_conn(conn)
        
        top_html="".join(f'<div class="item {"critico" if t["prioridade"]=="critica" else "alta"}"><h4>{t["titulo"]}</h4><p>Prioridade: {t["prioridade"]}</p></div>' for t in top)
        bl_html="".join(f'<div class="item critico"><h4>{b["titulo"]}</h4><p>{b.get("problema","")}</p></div>' for b in bl)
        
        total=pend+conc
        pct=int((conc/total)*100) if total else 0
        
        corpo=f"""
        {_topo("g")}
        <div class="container">
            <div class="bloco">
                <h2>STATUS GERAL</h2>
                <div style="font-size:36px;color:#00d97e;font-family:monospace;font-weight:700;margin-top:8px">{pct}%</div>
                <div class="barra"><div class="barra-p" style="width:{pct}%"></div></div>
                <p class="texto-cinza" style="margin-top:8px">{conc} de {total} tarefas concluidas</p>
            </div>
            <div class="grid">
                <div class="card"><h3>Tarefas Pendentes</h3><div class="v">{pend}</div></div>
                <div class="card"><h3>Concluidas</h3><div class="v">{conc}</div></div>
                <div class="card"><h3>Bloqueios Abertos</h3><div class="v" style="color:#ff5555">{bloq}</div></div>
                <div class="card"><h3>Projetos Ativos</h3><div class="v">{proj}</div></div>
                <div class="card"><h3>Metas Ativas</h3><div class="v">{metas}</div></div>
                <div class="card"><h3>MRR</h3><div class="v" style="font-size:20px">R$ {mrr:.2f}</div></div>
            </div>
            <div class="bloco"><h2>TOP 5 PRIORIDADES</h2>{top_html if top_html else "<p class=texto-cinza>Nada pendente.</p>"}</div>
            <div class="bloco"><h2>BLOQUEIOS ATIVOS</h2>{bl_html if bl_html else "<p class=texto-cinza>Nenhum bloqueio.</p>"}</div>
        </div>
        """
        return HTMLResponse(_html("Gestao", corpo))
