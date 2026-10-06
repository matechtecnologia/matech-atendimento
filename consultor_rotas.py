# consultor_rotas.py
# M.A Tech — Rotas da Consultoria Empresarial
# Por enquanto so uma rota de teste pra confirmar o registro.
# As rotas reais entram nas Etapas 2, 3 e 4.


def registrar_rotas_consultor(app, get_conn, close_conn, Cookie, Request):
    """Registra as rotas da Consultoria no app."""

    @app.get("/consultoria/ping")
    def consultoria_ping():
        return {"status": "ok", "area": "consultoria", "versao": "0.1"}