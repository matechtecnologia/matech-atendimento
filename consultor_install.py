# consultor_install.py atualizado com loading
def instalar_consultor(app, get_conn, close_conn, Cookie, Request):
    """Inicializa o banco e registra as rotas da Consultoria."""

    # 1. Cria as tabelas
    try:
        import consultor_db
        consultor_db.inicializar_consultor(get_conn, close_conn)
    except Exception as e:
        print(f"Consultor DB erro: {e}")

    # 2. Registra as rotas da Consultoria
    try:
        import consultor_rotas
        consultor_rotas.registrar_rotas_consultor(app, get_conn, close_conn, Cookie, Request)
        print("Consultor: rotas registradas")
    except Exception as e:
        print(f"Consultor rotas erro: {e}")

    # 3. Registra a tela de loading
    try:
        import consultor_loading
        consultor_loading.registrar_loading(app, Cookie)
        print("Consultor: rota de loading registrada")
    except Exception as e:
        print(f"Consultor loading erro: {e}")
