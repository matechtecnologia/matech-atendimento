# ============================================
# M.A Tech - Rotas Gestao Pessoal do Tempo
# ============================================
from fastapi import Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from datetime import date, timedelta

import gestao_tempo_db as db
import gestao_tempo_ia as ia
import gestao_tempo_notif as notif


def _ctx_base(nome, tipo):
    return {"usuario_nome": nome or "", "usuario_tipo": tipo or "", "hoje": date.today().isoformat()}


def instalar_gestao_tempo(app, templates, ler_sessao_func):

    def _uid(u):
        try: return int(u) if u else None
        except: return None

    def _ctx(un, ut, **extra):
        d = _ctx_base(un, ut)
        d.update(extra)
        return d

    # ---------------- CRON ----------------
    @app.get("/gestao/pessoal/tempo/_cron")
    def gt_cron():
        try:
            return JSONResponse(notif.verificar_e_enviar())
        except Exception as e:
            return JSONResponse({"ok": False, "erro": str(e)}, status_code=500)

    # ---------------- PAINEL (HOJE) ----------------
    @app.get("/gestao/pessoal/tempo", response_class=HTMLResponse)
    def gt_painel(request: Request, usuario_id: str = Cookie(None),
                  usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        hoje = date.today()
        return templates.TemplateResponse(request=request, name="gestao_tempo_painel.html",
            context=_ctx(usuario_nome, usuario_tipo,
                compromissos=db.listar_compromissos_dia(uid, hoje),
                rotinas=db.listar_rotinas(uid, apenas_ativas=True),
                bloqueios=db.listar_bloqueios_dia(uid, hoje),
                sugestoes=ia.gerar_sugestoes(uid),
                data_hoje=hoje.isoformat()))

    # ---------------- PLANEJADO ----------------
    @app.get("/gestao/pessoal/tempo/planejado", response_class=HTMLResponse)
    def gt_planejado(request: Request, usuario_id: str = Cookie(None),
                     usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        hoje = date.today()
        fim = hoje + timedelta(days=365)
        comps = db.listar_compromissos_semana(uid, hoje, fim)
        futuros = [c for c in comps if not c.get("concluido")]
        return templates.TemplateResponse(request=request, name="gestao_tempo_planejado.html",
            context=_ctx(usuario_nome, usuario_tipo, compromissos=futuros))

    # ---------------- SEMANA ----------------
    @app.get("/gestao/pessoal/tempo/semana", response_class=HTMLResponse)
    def gt_semana(request: Request, usuario_id: str = Cookie(None),
                  usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        hoje = date.today()
        data_inicio = hoje
        data_fim = hoje + timedelta(days=6)
        comps = db.listar_compromissos_semana(uid, data_inicio, data_fim)
        dias_map = {}
        cur = data_inicio
        while cur <= data_fim:
            dias_map[cur] = []
            cur += timedelta(days=1)
        for c in comps:
            d = c["data"]
            if d in dias_map: dias_map[d].append(c)
        dias = []
        for d in sorted(dias_map.keys()):
            dias.append({
                "data": d.isoformat(),
                "label": f"{['Seg','Ter','Qua','Qui','Sex','Sab','Dom'][d.weekday()]} {d.strftime('%d/%m')}",
                "compromissos": dias_map[d],
            })
        return templates.TemplateResponse(request=request, name="gestao_tempo_semana.html",
            context=_ctx(usuario_nome, usuario_tipo,
                dias=dias,
                data_inicio=data_inicio.strftime("%d/%m/%Y"),
                data_fim=data_fim.strftime("%d/%m/%Y")))

    # ---------------- NOVO ----------------
    @app.get("/gestao/pessoal/tempo/novo", response_class=HTMLResponse)
    def gt_novo_form(request: Request, usuario_id: str = Cookie(None),
                     usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        qs = request.query_params
        pre = {
            "titulo": qs.get("titulo", ""),
            "data": qs.get("data", ""),
            "hora_inicio": qs.get("hora_inicio", ""),
            "hora_fim": qs.get("hora_fim", ""),
        }
        return templates.TemplateResponse(request=request, name="gestao_tempo_novo.html",
            context=_ctx(usuario_nome, usuario_tipo, compromisso=None, pre=pre))

    @app.post("/gestao/pessoal/tempo/novo")
    def gt_novo_salvar(usuario_id: str = Cookie(None),
                       titulo: str = Form(...), data: str = Form(...),
                       hora_inicio: str = Form(""), hora_fim: str = Form(""),
                       descricao: str = Form(""), local: str = Form(""),
                       categoria: str = Form(""), prioridade: str = Form("media")):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        db.salvar_compromisso(uid, titulo, data, hora_inicio or None, hora_fim or None,
            descricao or None, local or None, categoria or None, prioridade or "media")
        return RedirectResponse("/gestao/pessoal/tempo", status_code=303)

    # ---------------- EDITAR ----------------
    @app.get("/gestao/pessoal/tempo/compromisso/{cid}", response_class=HTMLResponse)
    def gt_editar_form(cid: int, request: Request, usuario_id: str = Cookie(None),
                       usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        comp = db.obter_compromisso(uid, cid)
        if not comp: return RedirectResponse("/gestao/pessoal/tempo", status_code=303)
        return templates.TemplateResponse(request=request, name="gestao_tempo_novo.html",
            context=_ctx(usuario_nome, usuario_tipo, compromisso=comp))

    @app.post("/gestao/pessoal/tempo/compromisso/{cid}")
    def gt_editar_salvar(cid: int, usuario_id: str = Cookie(None),
                         titulo: str = Form(...), data: str = Form(...),
                         hora_inicio: str = Form(""), hora_fim: str = Form(""),
                         descricao: str = Form(""), local: str = Form(""),
                         categoria: str = Form(""), prioridade: str = Form("media")):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        db.editar_compromisso(uid, cid, titulo, data, hora_inicio or None, hora_fim or None,
            descricao or None, local or None, categoria or None, prioridade or "media")
        return RedirectResponse("/gestao/pessoal/tempo", status_code=303)

    @app.post("/gestao/pessoal/tempo/compromisso/{cid}/deletar")
    def gt_deletar(cid: int, usuario_id: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        db.deletar_compromisso(uid, cid)
        return RedirectResponse("/gestao/pessoal/tempo", status_code=303)

    @app.post("/gestao/pessoal/tempo/compromisso/{cid}/concluir")
    def gt_concluir(cid: int, usuario_id: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        db.marcar_compromisso_concluido(uid, cid, True)
        return RedirectResponse("/gestao/pessoal/tempo", status_code=303)

    # ---------------- ROTINAS ----------------
    @app.get("/gestao/pessoal/tempo/rotinas", response_class=HTMLResponse)
    def gt_rotinas(request: Request, usuario_id: str = Cookie(None),
                   usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        return templates.TemplateResponse(request=request, name="gestao_tempo_rotinas.html",
            context=_ctx(usuario_nome, usuario_tipo, rotinas=db.listar_rotinas(uid, apenas_ativas=False)))

    @app.post("/gestao/pessoal/tempo/rotinas/nova")
    def gt_rotina_nova(usuario_id: str = Cookie(None),
                       titulo: str = Form(...), dia_semana: int = Form(...),
                       hora_inicio: str = Form(""), hora_fim: str = Form(""),
                       categoria: str = Form("")):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        db.salvar_rotina(uid, titulo, dia_semana, hora_inicio or None, hora_fim or None, categoria or None)
        return RedirectResponse("/gestao/pessoal/tempo/rotinas", status_code=303)

    @app.post("/gestao/pessoal/tempo/rotinas/{rid}/toggle")
    def gt_rotina_toggle(rid: int, usuario_id: str = Cookie(None), ativo: str = Form("0")):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        db.alternar_rotina(uid, rid, ativo == "1")
        return RedirectResponse("/gestao/pessoal/tempo/rotinas", status_code=303)

    @app.post("/gestao/pessoal/tempo/rotinas/{rid}/deletar")
    def gt_rotina_deletar(rid: int, usuario_id: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        db.deletar_rotina(uid, rid)
        return RedirectResponse("/gestao/pessoal/tempo/rotinas", status_code=303)

    # ---------------- FOCO ----------------
    @app.get("/gestao/pessoal/tempo/foco", response_class=HTMLResponse)
    def gt_foco(request: Request, usuario_id: str = Cookie(None),
                usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        hoje = date.today()
        return templates.TemplateResponse(request=request, name="gestao_tempo_foco.html",
            context=_ctx(usuario_nome, usuario_tipo,
                bloqueios=db.listar_bloqueios_dia(uid, hoje),
                data_hoje=hoje.isoformat()))

    @app.post("/gestao/pessoal/tempo/foco/novo")
    def gt_foco_novo(usuario_id: str = Cookie(None),
                     titulo: str = Form("Foco"), data: str = Form(...),
                     hora_inicio: str = Form(...), hora_fim: str = Form(...)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        db.bloquear_foco(uid, data, hora_inicio, hora_fim, titulo or "Foco")
        return RedirectResponse("/gestao/pessoal/tempo/foco", status_code=303)

    @app.post("/gestao/pessoal/tempo/foco/{bid}/deletar")
    def gt_foco_deletar(bid: int, usuario_id: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        db.deletar_bloqueio(uid, bid)
        return RedirectResponse("/gestao/pessoal/tempo/foco", status_code=303)

    # ---------------- CONFIG ----------------
    @app.get("/gestao/pessoal/tempo/config", response_class=HTMLResponse)
    def gt_config(request: Request, usuario_id: str = Cookie(None),
                  usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        return templates.TemplateResponse(request=request, name="gestao_tempo_config.html",
            context=_ctx(usuario_nome, usuario_tipo, cfg=db.obter_config_notif(uid)))

    @app.post("/gestao/pessoal/tempo/config")
    async def gt_config_salvar(request: Request, usuario_id: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        form = await request.form()
        def _b(k): return form.get(k) == "on"
        def _i(k, d):
            try: return int(form.get(k, d))
            except: return d
        db.atualizar_config_notif(uid, {
            "notif_compromissos": _b("notif_compromissos"),
            "notif_rotinas": _b("notif_rotinas"),
            "notif_foco": _b("notif_foco"),
            "notif_sugestoes": _b("notif_sugestoes"),
            "minutos_antes": _i("minutos_antes", 15),
            "canal_push": _b("canal_push"),
            "canal_whatsapp": _b("canal_whatsapp"),
            "canal_email": _b("canal_email"),
            "canal_ligacao": _b("canal_ligacao"),
        })
        return RedirectResponse("/gestao/pessoal/tempo/config", status_code=303)

    # ---------------- HISTORICO ----------------
    @app.get("/gestao/pessoal/tempo/historico", response_class=HTMLResponse)
    def gt_historico(request: Request, usuario_id: str = Cookie(None),
                     usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid: return RedirectResponse("/login", status_code=303)
        return templates.TemplateResponse(request=request, name="gestao_tempo_historico.html",
            context=_ctx(usuario_nome, usuario_tipo, notificacoes=db.listar_notificacoes(uid, limite=100)))
