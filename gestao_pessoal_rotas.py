# ============================================
# M.A Tech - Rotas Gestao Pessoal Financeira
# ============================================
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import date

from gestao_pessoal_db import (
    CATEGORIAS_ENTRADA,
    CATEGORIAS_SAIDA_ESSENCIAL,
    CATEGORIAS_SAIDA_NAO_ESSENCIAL,
)


def _conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def instalar_gestao_pessoal(app, templates, ler_sessao_func):
    """Registra as rotas da Gestao Pessoal Financeira."""

    def _uid(usuario_id):
        """Recebe o usuario_id injetado pelo middleware. Retorna int ou None."""
        if not usuario_id:
            return None
        try:
            return int(usuario_id)
        except Exception:
            return None

    @app.get("/gestao/pessoal/financeira", response_class=HTMLResponse)
    def gp_painel(request: Request, usuario_id: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid:
            return RedirectResponse("/login", status_code=303)

        with _conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM gestao_pessoal_lancamentos
                    WHERE usuario_id = %s
                    ORDER BY data DESC, id DESC LIMIT 5
                """, (uid,))
                ultimos = cur.fetchall()

                cur.execute("""
                    SELECT
                      COALESCE(SUM(CASE WHEN tipo='entrada' THEN valor ELSE 0 END), 0) AS total_entrada,
                      COALESCE(SUM(CASE WHEN tipo='saida' THEN valor ELSE 0 END), 0) AS total_saida
                    FROM gestao_pessoal_lancamentos
                    WHERE usuario_id = %s
                      AND DATE_TRUNC('month', data) = DATE_TRUNC('month', CURRENT_DATE)
                """, (uid,))
                resumo = cur.fetchone()

                cur.execute("SELECT * FROM gestao_pessoal_metas WHERE usuario_id = %s ORDER BY id DESC LIMIT 3", (uid,))
                metas = cur.fetchall()

                cur.execute("SELECT * FROM gestao_pessoal_reserva WHERE usuario_id = %s", (uid,))
                reserva = cur.fetchone()

        saldo = float(resumo["total_entrada"]) - float(resumo["total_saida"])

        return templates.TemplateResponse(request=request, name="gestao_pessoal_financeira.html", context={
            "ultimos": [dict(l) for l in ultimos],
            "total_entrada": float(resumo["total_entrada"]),
            "total_saida": float(resumo["total_saida"]),
            "saldo": saldo,
            "metas": [dict(m) for m in metas],
            "reserva": dict(reserva) if reserva else None,
        })


    @app.get("/gestao/pessoal/financeira/lancar", response_class=HTMLResponse)
    def gp_lancar_form(request: Request, usuario_id: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid:
            return RedirectResponse("/login", status_code=303)
        return templates.TemplateResponse(request=request, name="gestao_pessoal_lancar.html", context={
            "categorias_entrada": CATEGORIAS_ENTRADA,
            "categorias_essencial": CATEGORIAS_SAIDA_ESSENCIAL,
            "categorias_nao_essencial": CATEGORIAS_SAIDA_NAO_ESSENCIAL,
            "hoje": date.today().isoformat(),
        })


    @app.post("/gestao/pessoal/financeira/lancar")
    def gp_lancar_salvar(
        tipo: str = Form(...),
        valor: float = Form(...),
        categoria: str = Form(...),
        essencial: str = Form(None),
        descricao: str = Form(""),
        usuario_id: str = Cookie(None),
        data_lanc: str = Form(None),
    ):
        uid = _uid(usuario_id)
        if not uid:
            return RedirectResponse("/login", status_code=303)

        d = data_lanc if data_lanc else date.today().isoformat()
        ess = bool(essencial)

        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO gestao_pessoal_lancamentos
                    (usuario_id, tipo, valor, categoria, essencial, descricao, data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (uid, tipo, valor, categoria, ess, descricao, d))
            conn.commit()

        return RedirectResponse("/gestao/pessoal/financeira", status_code=303)


    @app.get("/gestao/pessoal/financeira/extrato", response_class=HTMLResponse)
    def gp_extrato(request: Request, tipo: str = None, categoria: str = None, usuario_id: str = Cookie(None)):
        uid = _uid(usuario_id)
        if not uid:
            return RedirectResponse("/login", status_code=303)

        where = "WHERE usuario_id = %s"
        params = [uid]
        if tipo in ("entrada", "saida"):
            where += " AND tipo = %s"
            params.append(tipo)
        if categoria:
            where += " AND categoria = %s"
            params.append(categoria)

        with _conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(f"""
                    SELECT * FROM gestao_pessoal_lancamentos
                    {where}
                    ORDER BY data DESC, id DESC LIMIT 100
                """, tuple(params))
                lancamentos = cur.fetchall()

        todas_categorias = CATEGORIAS_ENTRADA + CATEGORIAS_SAIDA_ESSENCIAL + CATEGORIAS_SAIDA_NAO_ESSENCIAL

        return templates.TemplateResponse(request=request, name="gestao_pessoal_extrato.html", context={
            "lancamentos": [dict(l) for l in lancamentos],
            "tipo_atual": tipo or "",
            "categoria_atual": categoria or "",
            "todas_categorias": todas_categorias,
        })
