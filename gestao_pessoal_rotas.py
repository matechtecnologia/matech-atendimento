# ============================================
# M.A Tech - Rotas Gestao Pessoal Financeira
# ============================================
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from datetime import date

from gestao_pessoal_db import (
    CATEGORIAS_ENTRADA, CATEGORIAS_SAIDA_ESSENCIAL, CATEGORIAS_SAIDA_NAO_ESSENCIAL, TIPOS_CAIXINHA,
)

def _conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def instalar_gestao_pessoal(app, templates, ler_sessao_func):
    def _uid(u):
        try: return int(u) if u else None
        except: return None

    def _ctx(un, ut, aba):
        return {"usuario_nome": un or "", "usuario_tipo": ut or "", "aba_ativa": aba, "hoje": date.today().isoformat()}

    def _caixinhas(cur, uid):
        for t in TIPOS_CAIXINHA:
            cur.execute("INSERT INTO gestao_caixinhas (usuario_id, tipo, valor_atual) VALUES (%s,%s,0) ON CONFLICT (usuario_id,tipo) DO NOTHING", (uid,t))

    def _prefs(cur, uid):
        cur.execute("INSERT INTO gestao_pessoal_preferencias (usuario_id) VALUES (%s) ON CONFLICT (usuario_id) DO NOTHING", (uid,))

    def _saldo(cur, uid):
        cur.execute("SELECT COALESCE(SUM(CASE WHEN tipo='entrada' THEN valor ELSE -valor END),0) AS s FROM gestao_pessoal_lancamentos WHERE usuario_id=%s AND status='concluido'", (uid,))
        return float(cur.fetchone()["s"])

    @app.get("/gestao/pessoal/financeira", response_class=HTMLResponse)
    def gp_painel(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        with _conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                _caixinhas(cur, uid); _prefs(cur, uid); conn.commit()
                cur.execute("SELECT * FROM gestao_pessoal_lancamentos WHERE usuario_id=%s AND status='concluido' ORDER BY data DESC, id DESC LIMIT 5", (uid,))
                ultimos = cur.fetchall()
                cur.execute("SELECT COALESCE(SUM(CASE WHEN tipo='entrada' THEN valor ELSE 0 END),0) AS te, COALESCE(SUM(CASE WHEN tipo='saida' THEN valor ELSE 0 END),0) AS ts FROM gestao_pessoal_lancamentos WHERE usuario_id=%s AND status='concluido' AND DATE_TRUNC('month',data)=DATE_TRUNC('month',CURRENT_DATE)", (uid,))
                r = cur.fetchone()
                saldo_total = _saldo(cur, uid)
                cur.execute("SELECT COUNT(*) AS q, COALESCE(SUM(CASE WHEN tipo='entrada' THEN valor ELSE -valor END),0) AS t FROM gestao_pessoal_lancamentos WHERE usuario_id=%s AND status='planejado'", (uid,))
                pl = cur.fetchone()
                cur.execute("SELECT * FROM gestao_caixinhas WHERE usuario_id=%s ORDER BY tipo", (uid,))
                cx = {x["tipo"]: dict(x) for x in cur.fetchall()}
                cur.execute("SELECT * FROM gestao_pessoal_preferencias WHERE usuario_id=%s", (uid,))
                pr = dict(cur.fetchone())
                cur.execute("SELECT * FROM gestao_aplicacoes WHERE usuario_id=%s ORDER BY data DESC, id DESC LIMIT 20", (uid,))
                ap = [dict(a) for a in cur.fetchall()]
                cur.execute("SELECT * FROM gestao_pessoal_metas WHERE usuario_id=%s ORDER BY id DESC LIMIT 3", (uid,))
                metas = cur.fetchall()
        te, ts = float(r["te"]), float(r["ts"])
        pe, pi = float(pr["percentual_emergencia"]), float(pr["percentual_investimento"])
        ve, vi = saldo_total*(pe/100), saldo_total*(pi/100)
        ult = {}
        for a in ap:
            if a["caixinha_tipo"] not in ult: ult[a["caixinha_tipo"]] = a
        ctx = _ctx(usuario_nome, usuario_tipo, "financeiro")
        ctx.update({"ultimos":[dict(l) for l in ultimos],"total_entrada":te,"total_saida":ts,"saldo":te-ts,"saldo_total":saldo_total,"planejado_qtd":int(pl["q"]),"planejado_total":float(pl["t"]),"caixinhas":cx,"prefs":pr,"pct_em":pe,"pct_inv":pi,"val_em":ve,"val_inv":vi,"val_combo":ve+vi,"ultima_aplic":ult,"metas":[dict(m) for m in metas]})
        return templates.TemplateResponse(request=request, name="gestao_pessoal_financeira.html", context=ctx)

    @app.get("/gestao/pessoal/financeira/lancar", response_class=HTMLResponse)
    def gp_lancar_form(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        ctx = _ctx(usuario_nome, usuario_tipo, "financeiro")
        ctx.update({"categorias_entrada":CATEGORIAS_ENTRADA,"categorias_essencial":CATEGORIAS_SAIDA_ESSENCIAL,"categorias_nao_essencial":CATEGORIAS_SAIDA_NAO_ESSENCIAL})
        return templates.TemplateResponse(request=request, name="gestao_pessoal_lancar.html", context=ctx)

    @app.post("/gestao/pessoal/financeira/lancar")
    def gp_lancar_salvar(tipo: str = Form(...), valor: float = Form(...), categoria: str = Form(...), essencial: str = Form(None), descricao: str = Form(""), status_lanc: str = Form("concluido"), usuario_id: str = Cookie(None), data_lanc: str = Form(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        d = data_lanc or date.today().isoformat()
        st = status_lanc if status_lanc in ("concluido","planejado") else "concluido"
        dp = d if st=="planejado" else None
        dc = d if st=="concluido" else None
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO gestao_pessoal_lancamentos (usuario_id,tipo,valor,categoria,essencial,descricao,data,status,data_prevista,data_conclusao) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (uid,tipo,valor,categoria,bool(essencial),descricao,d,st,dp,dc))
            conn.commit()
        return RedirectResponse("/gestao/pessoal/financeira/planejado" if st=="planejado" else "/gestao/pessoal/financeira", status_code=303)

    @app.get("/gestao/pessoal/financeira/extrato", response_class=HTMLResponse)
    def gp_extrato(request: Request, tipo: str = None, categoria: str = None, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        w = "WHERE usuario_id=%s AND status='concluido'"; p = [uid]
        if tipo in ("entrada","saida"): w+=" AND tipo=%s"; p.append(tipo)
        if categoria: w+=" AND categoria=%s"; p.append(categoria)
        with _conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(f"SELECT * FROM gestao_pessoal_lancamentos {w} ORDER BY data DESC, id DESC LIMIT 100", tuple(p))
                ls = cur.fetchall()
        tc = CATEGORIAS_ENTRADA + CATEGORIAS_SAIDA_ESSENCIAL + CATEGORIAS_SAIDA_NAO_ESSENCIAL
        ctx = _ctx(usuario_nome, usuario_tipo, "financeiro")
        ctx.update({"lancamentos":[dict(l) for l in ls],"tipo_atual":tipo or "","categoria_atual":categoria or "","todas_categorias":tc})
        return templates.TemplateResponse(request=request, name="gestao_pessoal_extrato.html", context=ctx)

    @app.post("/gestao/pessoal/financeira/lancamento/deletar")
    def gp_del(lanc_id: int = Form(...), usuario_id: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        with _conn() as conn:
            with conn.cursor() as cur: cur.execute("DELETE FROM gestao_pessoal_lancamentos WHERE id=%s AND usuario_id=%s", (lanc_id, uid))
            conn.commit()
        return RedirectResponse("/gestao/pessoal/financeira/extrato", status_code=303)

    @app.post("/gestao/pessoal/financeira/lancamento/editar")
    def gp_edit(lanc_id: int = Form(...), tipo: str = Form(...), valor: float = Form(...), categoria: str = Form(...), descricao: str = Form(""), data_lanc: str = Form(...), usuario_id: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE gestao_pessoal_lancamentos SET tipo=%s,valor=%s,categoria=%s,descricao=%s,data=%s WHERE id=%s AND usuario_id=%s", (tipo,valor,categoria,descricao,data_lanc,lanc_id,uid))
            conn.commit()
        return RedirectResponse("/gestao/pessoal/financeira/extrato", status_code=303)

    @app.get("/gestao/pessoal/financeira/planejado", response_class=HTMLResponse)
    def gp_plan(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        with _conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM gestao_pessoal_lancamentos WHERE usuario_id=%s AND status='planejado' ORDER BY data_prevista ASC NULLS LAST, id DESC", (uid,))
                it = cur.fetchall()
        ctx = _ctx(usuario_nome, usuario_tipo, "planejado")
        ctx.update({"itens":[dict(i) for i in it],"total":sum(float(i["valor"]) for i in it)})
        return templates.TemplateResponse(request=request, name="gestao_pessoal_planejado.html", context=ctx)

    @app.post("/gestao/pessoal/financeira/planejado/concluir")
    def gp_plan_conc(lanc_id: int = Form(...), data_conclusao: str = Form(...), usuario_id: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid or not data_conclusao: return RedirectResponse("/gestao/pessoal/financeira/planejado", status_code=303)
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE gestao_pessoal_lancamentos SET status='concluido',data=%s,data_conclusao=%s WHERE id=%s AND usuario_id=%s AND status='planejado'", (data_conclusao,data_conclusao,lanc_id,uid))
            conn.commit()
        return RedirectResponse("/gestao/pessoal/financeira/planejado", status_code=303)

    @app.post("/gestao/pessoal/financeira/planejado/deletar")
    def gp_plan_del(lanc_id: int = Form(...), usuario_id: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        with _conn() as conn:
            with conn.cursor() as cur: cur.execute("DELETE FROM gestao_pessoal_lancamentos WHERE id=%s AND usuario_id=%s AND status='planejado'", (lanc_id, uid))
            conn.commit()
        return RedirectResponse("/gestao/pessoal/financeira/planejado", status_code=303)

    @app.get("/gestao/pessoal/financeira/caixinha", response_class=HTMLResponse)
    def gp_cx(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        with _conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                _caixinhas(cur, uid); conn.commit()
                cur.execute("SELECT * FROM gestao_caixinhas WHERE usuario_id=%s ORDER BY tipo", (uid,))
                cx = [dict(c) for c in cur.fetchall()]
                cur.execute("SELECT * FROM gestao_aplicacoes WHERE usuario_id=%s ORDER BY data DESC, id DESC LIMIT 20", (uid,))
                ap = [dict(a) for a in cur.fetchall()]
                st = _saldo(cur, uid)
        ctx = _ctx(usuario_nome, usuario_tipo, "caixinha")
        ctx.update({"caixinhas":cx,"aplicacoes":ap,"saldo_total":st,"total_guardado":sum(float(c["valor_atual"]) for c in cx)})
        return templates.TemplateResponse(request=request, name="gestao_pessoal_caixinha.html", context=ctx)

    @app.post("/gestao/pessoal/financeira/caixinha/aplicar")
    def gp_cx_apl(tipo: str = Form(...), valor: float = Form(...), instituicao: str = Form(...), data_ap: str = Form(...), porcentagem: str = Form(None), usuario_id: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid or tipo not in TIPOS_CAIXINHA or valor<=0 or not data_ap or not instituicao: return RedirectResponse("/gestao/pessoal/financeira/caixinha", status_code=303)
        pct = None
        if porcentagem:
            try: pct = float(porcentagem)
            except: pct = None
        with _conn() as conn:
            with conn.cursor() as cur:
                _caixinhas(cur, uid)
                cur.execute("UPDATE gestao_caixinhas SET valor_atual=valor_atual+%s, instituicao_financeira=%s WHERE usuario_id=%s AND tipo=%s", (valor,instituicao,uid,tipo))
                cur.execute("INSERT INTO gestao_pessoal_lancamentos (usuario_id,tipo,valor,categoria,essencial,descricao,data,status,data_conclusao) VALUES (%s,'saida',%s,'Aplicação',FALSE,%s,%s,'concluido',%s)", (uid,valor,f"Aplicação caixinha {tipo}",data_ap,data_ap))
                cur.execute("INSERT INTO gestao_aplicacoes (usuario_id,caixinha_tipo,valor,porcentagem_aplicada,instituicao_financeira,data) VALUES (%s,%s,%s,%s,%s,%s)", (uid,tipo,valor,pct,instituicao,data_ap))
            conn.commit()
        return RedirectResponse("/gestao/pessoal/financeira/caixinha", status_code=303)

    @app.post("/gestao/pessoal/financeira/caixinha/resgatar")
    def gp_cx_res(tipo: str = Form(...), valor: float = Form(...), data_res: str = Form(...), motivo: str = Form(""), forcar: str = Form(None), usuario_id: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid or tipo not in TIPOS_CAIXINHA or valor<=0 or not data_res: return RedirectResponse("/gestao/pessoal/financeira/caixinha", status_code=303)
        with _conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT valor_atual FROM gestao_caixinhas WHERE usuario_id=%s AND tipo=%s", (uid,tipo))
                r = cur.fetchone()
                if not r or float(r["valor_atual"])<valor: return RedirectResponse("/gestao/pessoal/financeira/caixinha", status_code=303)
                cur.execute("UPDATE gestao_caixinhas SET valor_atual=valor_atual-%s WHERE usuario_id=%s AND tipo=%s", (valor,uid,tipo))
                cur.execute("INSERT INTO gestao_pessoal_lancamentos (usuario_id,tipo,valor,categoria,essencial,descricao,data,status,data_conclusao) VALUES (%s,'entrada',%s,'Resgate',FALSE,%s,%s,'concluido',%s)", (uid,valor,f"Resgate caixinha {tipo}"+(f" - {motivo}" if motivo else ""),data_res,data_res))
            conn.commit()
        return RedirectResponse("/gestao/pessoal/financeira/caixinha", status_code=303)

    @app.post("/gestao/pessoal/financeira/editar-percentual")
    def gp_pct(tipo: str = Form(...), percentual: float = Form(...), usuario_id: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return JSONResponse({"ok":False}, status_code=401)
        if tipo not in ("emergencia","investimento") or percentual<0 or percentual>100: return JSONResponse({"ok":False}, status_code=400)
        col = "percentual_emergencia" if tipo=="emergencia" else "percentual_investimento"
        with _conn() as conn:
            with conn.cursor() as cur:
                _prefs(cur, uid)
                cur.execute(f"UPDATE gestao_pessoal_preferencias SET {col}=%s, atualizado_em=NOW() WHERE usuario_id=%s", (percentual,uid))
            conn.commit()
        return JSONResponse({"ok":True,"percentual":percentual})

    @app.post("/gestao/pessoal/financeira/aplicar")
    def gp_apl(tipo: str = Form(...), percentual: float = Form(...), data_ap: str = Form(...), banco: str = Form(...), usuario_id: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return JSONResponse({"ok":False}, status_code=401)
        if tipo not in ("emergencia","investimento","combo") or not data_ap or not banco or percentual<=0 or percentual>100: return JSONResponse({"ok":False}, status_code=400)
        with _conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                _caixinhas(cur, uid); _prefs(cur, uid)
                s = _saldo(cur, uid)
                if s<=0: return JSONResponse({"ok":False,"erro":"saldo_insuficiente"}, status_code=400)
                movs = []
                if tipo=="emergencia":
                    v=s*(percentual/100)
                    if v>0: movs.append(("emergencia",v,percentual))
                elif tipo=="investimento":
                    v=s*(percentual/100)
                    if v>0: movs.append(("investimento",v,percentual))
                else:
                    cur.execute("SELECT * FROM gestao_pessoal_preferencias WHERE usuario_id=%s", (uid,))
                    p=cur.fetchone()
                    pe,pi = float(p["percentual_emergencia"]),float(p["percentual_investimento"])
                    if pe+pi<=0: return JSONResponse({"ok":False}, status_code=400)
                    ve,vi = s*(pe/100),s*(pi/100)
                    if ve>0: movs.append(("emergencia",ve,pe))
                    if vi>0: movs.append(("investimento",vi,pi))
                if not movs: return JSONResponse({"ok":False}, status_code=400)
                for ct,cv,cp in movs:
                    cur.execute("UPDATE gestao_caixinhas SET valor_atual=valor_atual+%s, instituicao_financeira=%s WHERE usuario_id=%s AND tipo=%s", (cv,banco,uid,ct))
                    cur.execute("INSERT INTO gestao_pessoal_lancamentos (usuario_id,tipo,valor,categoria,essencial,descricao,data,status,data_conclusao) VALUES (%s,'saida',%s,'Aplicação',FALSE,%s,%s,'concluido',%s)", (uid,cv,f"Aplicação {ct} ({cp:.0f}%) - {banco}",data_ap,data_ap))
                    cur.execute("INSERT INTO gestao_aplicacoes (usuario_id,caixinha_tipo,valor,porcentagem_aplicada,instituicao_financeira,data) VALUES (%s,%s,%s,%s,%s,%s)", (uid,ct,cv,cp,banco,data_ap))
            conn.commit()
        return JSONResponse({"ok":True})

    @app.get("/gestao/pessoal/financeira/dashboarding", response_class=HTMLResponse)
    def gp_dash(request: Request, data_ini: str = None, data_fim: str = None, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        di = data_ini or date.today().replace(day=1).isoformat()
        df = data_fim or date.today().isoformat()
        with _conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT categoria,tipo,SUM(valor) AS total FROM gestao_pessoal_lancamentos WHERE usuario_id=%s AND status='concluido' AND data BETWEEN %s AND %s GROUP BY categoria,tipo ORDER BY total DESC", (uid,di,df))
                pc = [dict(x) for x in cur.fetchall()]
                cur.execute("SELECT data,tipo,SUM(valor) AS total FROM gestao_pessoal_lancamentos WHERE usuario_id=%s AND status='concluido' AND data BETWEEN %s AND %s GROUP BY data,tipo ORDER BY data ASC", (uid,di,df))
                pd = [dict(x) for x in cur.fetchall()]
        ctx = _ctx(usuario_nome, usuario_tipo, "dashboarding")
        ctx.update({"data_ini":di,"data_fim":df,"por_categoria":pc,"por_dia":pd})
        return templates.TemplateResponse(request=request, name="gestao_pessoal_dashboarding.html", context=ctx)

    @app.get("/gestao/pessoal/financeira/socio", response_class=HTMLResponse)
    def gp_soc(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        return templates.TemplateResponse(request=request, name="gestao_pessoal_socio.html", context=_ctx(usuario_nome, usuario_tipo, "socio"))
