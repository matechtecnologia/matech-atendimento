# consultor_install.py atualizado com em_breve
def instalar_consultor(app, get_conn, close_conn, Cookie, Request):
    """Inicializa o banco e registra as rotas da Consultoria."""

    # 1. Cria as tabelas
    try:
        import consultor_db
        consultor_db.inicializar_consultor(get_conn, close_conn)
    except Exception as e:
        print(f"Consultor DB erro: {e}")

    # 2. Registra as rotas da Consultoria (versao atual - admin)
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

    # 4. Registra a tela "em desenvolvimento" (cliente ve isso)
    try:
        import consultor_em_breve
        consultor_em_breve.registrar_em_breve(app, Cookie)
        print("Consultor: rota em-breve registrada")
    except Exception as e:
        print(f"Consultor em-breve erro: {e}")

    # 5. Rota pra saber se e admin
    try:
        from fastapi.responses import JSONResponse
        @app.get("/api/eh-admin")
        def eh_admin(usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
            return JSONResponse({"admin": bool(usuario_id and usuario_tipo == "admin")})
        print("Consultor: rota eh-admin registrada")
    except Exception as e:
        print(f"Consultor eh-admin erro: {e}")
