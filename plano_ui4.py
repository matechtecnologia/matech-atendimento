# plano_ui4.py
# Telas de Pendencias e Proximos Passos

from fastapi.responses import RedirectResponse, HTMLResponse


CSS = """
body { background:#0a0a0a; color:#e8e8e8; font-family:-apple-system,BlinkMacSystemFont,sans-serif; margin:0; }
.topo { background:#0f1a15; padding:14px 20px; border-bottom:1px solid #00d97e33; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; }
.topo h1 { color:#00d97e; font-size:18px; margin:0; }
.menu { display:flex; gap:12px; flex-wrap:wrap; }
.menu a { color:#e8e8e8; text-decoration:none; font-size:13px; padding:6px 10px; border-radius:6px; }
.menu a:hover, .menu a.ativo { background:#00d97e22; color:#00d97e; }
.container { max-width:1100px; margin:20px auto; padding:0 20px; }
.bloco { background:#141414; border:1px solid #222; border-radius:8px; padding:18px; margin-bottom:14px; }
.bloco h2 { font-size:15px; margin:0 0 10px 0; color:#e8e8e8; }
.badge { display:inline-block; padding:3px 8px; border-radius:10px; font-size:10px; font-weight:700; text-transform:uppercase; }
.b-verde { background:#0a1f15; color:#00d97e; border:1px solid #00d97e; }
.b-amarelo { background:#1f1a0a; color:#f5c542; border:1px solid #f5c542; }
.b-vermelho { background:#1f0a0a; color:#ff5555; border:1px solid #ff5555; }
.b-cinza { background:#1a1a1a; color:#8a8a8a; border:1px solid #3a3a3a; }
.item { background:#141414; border:1px solid #222; border-left:3px solid #00d97e; border-radius:8px; padding:14px; margin-bottom:10px; }
.item.pendente { border-left-color:#f5c542; }
.item.pronto { border-left-color:#00d97e; }
.item.critico { border-left-color:#ff5555; }
.item h3 { font-size:14px; margin:0 0 6px 0; color:#e8e8e8; }
.item p { color:#8a8a8a; font-size:12px; margin:3px 0; }
.texto-cinza { color:#8a8a8a; font-size:13px; }
.numero { font-family:monospace; color:#00d97e; font-size:22px; font-weight:700; }
"""


def _auth(uid, tipo):
    return uid and tipo == "admin"


def _topo(ativo):
    itens = [
        ("/plano", "Dashboard", "dashboard"),
        ("/plano/fases", "Roadmap", "fases"),
        ("/plano/metas", "Metas", "metas"),
        ("/plano/tarefas", "Tarefas", "tarefas"),
        ("/plano/produtos", "Produtos", "produtos"),
        ("/plano/projetos", "Projetos", "projetos"),
        ("/plano/decisoes", "Decisoes", "decisoes"),
        ("/plano/bloqueios", "Bloqueios", "bloqueios"),
        ("/plano/pendencias", "Pendencias", "pendencias"),
        ("/plano/proximos", "Proximos", "proximos"),
        ("/plano/diario", "Diario", "diario"),
    ]
    menu = "".join(f'<a href="{h}" class="{"ativo" if ativo==k else ""}">{n}</a>' for h,n,k in itens)
    return f'<div class="topo"><h1>Plano M.A Tech</h1><div class="menu">{menu}</div></div>'


def _html(titulo, corpo):
    return f'<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{titulo}</title><style>{CSS}</style></head><body>{corpo}</body></html>'


def registrar_rotas_plano_ui4(app, get_conn, close_conn, Cookie, Request):
    from psycopg2.extras import RealDictCursor

    @app.get("/plano/pendencias", response_class=HTMLResponse)
    def plano_pendencias(usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT t.*, g.titulo as goal_titulo FROM tasks t LEFT JOIN goals g ON g.id = t.goal_id WHERE t.status IN ('pendente', 'em_andamento') ORDER BY CASE t.prioridade WHEN 'critica' THEN 1 WHEN 'alta' THEN 2 WHEN 'media' THEN 3 ELSE 4 END, t.id")
        tarefas = [dict(t) for t in cur.fetchall()]
        cur.execute("SELECT * FROM blockers WHERE status = 'aberto' ORDER BY prioridade, id")
        bloqueios = [dict(b) for b in cur.fetchall()]
        cur.close()
        close_conn(conn)

        html_b = "".join(
            f'<div class="item critico"><h3>{b["titulo"]} <span class="badge b-vermelho" style="float:right;">{b["prioridade"].upper()}</span></h3>'
            f'{f"<p>Problema: {b['problema']}</p>" if b.get("problema") else ""}'
            f'{f"<p>Solucao: {b['solucao_necessaria']}</p>" if b.get("solucao_necessaria") else ""}</div>'
            for b in bloqueios
        )

        html_t = ""
        for t in tarefas:
            prio = t.get("prioridade") or "media"
            cls = "critico" if prio == "critica" else ("pendente" if prio == "alta" else "")
            bc = {"critica": "b-vermelho", "alta": "b-amarelo", "media": "b-cinza"}.get(prio, "b-cinza")
            html_t += f'<div class="item {cls}"><h3>{t["titulo"]} <span class="badge {bc}" style="float:right;">{prio.upper()}</span></h3>'
            if t.get("descricao"): html_t += f'<p>{t["descricao"]}</p>'
            if t.get("goal_titulo"): html_t += f'<p>Meta: {t["goal_titulo"]}</p>'
            html_t += '</div>'

        corpo = f'{_topo("pendencias")}<div class="container">'
        corpo += f'<div class="bloco"><h2>PENDENCIAS</h2><div style="display:flex;gap:20px;margin-top:14px;"><div><div class="numero">{len(tarefas)}</div><div class="texto-cinza">Tarefas</div></div><div><div class="numero" style="color:#ff5555;">{len(bloqueios)}</div><div class="texto-cinza">Bloqueios</div></div></div></div>'
        corpo += f'<div class="bloco"><h2>BLOQUEIOS ATIVOS ({len(bloqueios)})</h2>{html_b if html_b else "<p class=texto-cinza>Nenhum.</p>"}</div>'
        corpo += f'<div class="bloco"><h2>TAREFAS PENDENTES ({len(tarefas)})</h2>{html_t if html_t else "<p class=texto-cinza>Nenhuma.</p>"}</div>'
        corpo += '</div>'
        return HTMLResponse(_html("Pendencias", corpo))

    @app.get("/plano/proximos", response_class=HTMLResponse)
    def plano_proximos(usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        if not _auth(usuario_id, usuario_tipo):
            return RedirectResponse(url="/login")
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT t.*, g.titulo as goal_titulo FROM tasks t LEFT JOIN goals g ON g.id = t.goal_id WHERE t.status IN ('pendente', 'em_andamento') ORDER BY CASE t.prioridade WHEN 'critica' THEN 1 WHEN 'alta' THEN 2 WHEN 'media' THEN 3 ELSE 4 END, t.id LIMIT 10")
        tarefas = [dict(t) for t in cur.fetchall()]
        cur.execute("SELECT * FROM goals WHERE status = 'em_andamento' ORDER BY prioridade LIMIT 5")
        metas = [dict(m) for m in cur.fetchall()]
        cur.execute("SELECT * FROM roadmap_phases WHERE status = 'em_execucao' ORDER BY numero LIMIT 1")
        fase = cur.fetchone()
        cur.close()
        close_conn(conn)

        html_p = ""
        for i, t in enumerate(tarefas, 1):
            prio = t.get("prioridade") or "media"
            cls = "critico" if prio == "critica" else ""
            html_p += f'<div class="item {cls}"><h3><span style="color:#00d97e;font-family:monospace;">#{i}</span> {t["titulo"]}</h3>'
            if t.get("descricao"): html_p += f'<p>{t["descricao"]}</p>'
            html_p += f'<p>Prioridade: {prio}</p></div>'

        html_m = "".join(
            f'<div class="item pronto"><h3>{m["titulo"]}</h3><p>{float(m["valor_atual"] or 0):.0f} / {float(m["valor_meta"] or 1):.0f} {m.get("unidade") or ""}</p></div>'
            for m in metas
        )

        fn = fase["nome"] if fase else "Sem fase"
        fd = fase["descricao"] if fase else ""

        corpo = f'{_topo("proximos")}<div class="container">'
        corpo += f'<div class="bloco"><h2>FASE ATUAL</h2><p style="font-size:18px;color:#00d97e;margin:6px 0;">{fn}</p><p class="texto-cinza">{fd}</p></div>'
        corpo += f'<div class="bloco"><h2>O QUE FAZER AGORA (Top 10)</h2>{html_p if html_p else "<p class=texto-cinza>Nada.</p>"}</div>'
        corpo += f'<div class="bloco"><h2>METAS EM ANDAMENTO ({len(metas)})</h2>{html_m if html_m else "<p class=texto-cinza>Nenhuma.</p>"}</div>'
        corpo += '</div>'
        return HTMLResponse(_html("Proximos Passos", corpo))
