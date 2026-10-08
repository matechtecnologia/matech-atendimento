def instalar_plano(app, get_conn, close_conn, Cookie, Request):
    import plano_db
    import plano_ui

    try:
        plano_db.inicializar_plano(get_conn, close_conn)
    except Exception as e:
        print(f"Plano DB erro: {e}")

    try:
        plano_ui.registrar_rotas_plano_ui(app, get_conn, close_conn, Cookie, Request)
        print("Plano: rotas principais registradas")
    except Exception as e:
        print(f"Plano rotas erro: {e}")

    try:
        import plano_ui2
        plano_ui2.registrar_rotas_plano_ui2(app, get_conn, close_conn, Cookie, Request)
        print("Plano: rotas extras registradas")
    except Exception as e:
        print(f"Plano rotas extras erro: {e}")

    try:
        import plano_ui3
        plano_ui3.registrar_rotas_plano_ui3(app, get_conn, close_conn, Cookie, Request)
        print("Plano: rotas comerciais registradas")
    except Exception as e:
        print(f"Plano rotas comerciais erro: {e}")

    try:
        import plano_ui4
        plano_ui4.registrar_rotas_plano_ui4(app, get_conn, close_conn, Cookie, Request)
        print("Plano: rotas pendencias/proximos registradas")
    except Exception as e:
        print(f"Plano rotas pendencias/proximos erro: {e}")

    try:
        import plano_roi
        plano_roi.registrar_rotas_roi(app, get_conn, close_conn, Cookie, Request)
        print("Plano: rotas ROI registradas")
    except Exception as e:
        print(f"Plano rotas ROI erro: {e}")
