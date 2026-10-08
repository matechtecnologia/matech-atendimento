def instalar_plano(app, get_conn, close_conn, Cookie, Request):
    import plano_db
    import plano_ui

    try:
        plano_db.inicializar_plano(get_conn, close_conn)
    except Exception as e:
        print(f"Plano DB erro: {e}")

    for mod, func in [
        ("plano_ui", "registrar_rotas_plano_ui"),
        ("plano_ui2", "registrar_rotas_plano_ui2"),
        ("plano_ui3", "registrar_rotas_plano_ui3"),
        ("plano_ui4", "registrar_rotas_plano_ui4"),
        ("plano_gestao", "registrar_rotas_gestao"),
        ("plano_roi", "registrar_rotas_roi"),
    ]:
        try:
            m = __import__(mod)
            getattr(m, func)(app, get_conn, close_conn, Cookie, Request)
            print(f"Plano: {mod} registrado")
        except Exception as e:
            print(f"Plano {mod} erro: {e}")
