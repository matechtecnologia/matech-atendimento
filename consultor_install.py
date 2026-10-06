# consultor_install.py
# M.A Tech — Instalador da Consultoria Empresarial
# Amarra o banco + as rotas no app.py.
# Chamado UMA vez, no app.py (do lado do instalar_plano).


def instalar_consultor(app, get_conn, close_conn, Cookie, Request):
    """Inicializa o banco e registra as rotas da Consultoria."""

    # 1. Cria as tabelas
    try:
        import consultor_db
        consultor_db.inicializar_consultor(get_conn, close_conn)
    except Exception as e:
        print(f"Consultor DB erro: {e}")

    # 2. Registra as rotas
    try:
        import consultor_rotas
        consultor_rotas.registrar_rotas_consultor(app, get_conn, close_conn, Cookie, Request)
    except Exception as e:
        print(f"Consultor rotas erro: {e}")