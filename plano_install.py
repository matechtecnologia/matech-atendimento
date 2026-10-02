# plano_install.py
# Conecta o painel M.A Tech ao app.py
# Uso: no app.py, adicione:
#   from plano_install import instalar_plano
#   instalar_plano(app, get_conn, close_conn, Cookie, Request)

def instalar_plano(app, get_conn, close_conn, Cookie, Request):
    import plano_db
    import plano_ui

    # 1. Cria tabelas (idempotente)
    try:
        plano_db.inicializar_plano(get_conn, close_conn)
    except Exception as e:
        print(f"Plano DB erro: {e}")

    # 2. Registra rotas principais
    try:
        plano_ui.registrar_rotas_plano_ui(app, get_conn, close_conn, Cookie, Request)
        print("Plano: rotas principais registradas")
    except Exception as e:
        print(f"Plano rotas erro: {e}")

    # 3. Registra rotas extras (produtos, projetos, decisoes, financeiro)
    try:
        import plano_ui2
        plano_ui2.registrar_rotas_plano_ui2(app, get_conn, close_conn, Cookie, Request)
        print("Plano: rotas extras registradas")
    except Exception as e:
        print(f"Plano rotas extras erro: {e}")

    # 4. Registra rotas comerciais, gestao, lab, relatorios
    try:
        import plano_ui3
        plano_ui3.registrar_rotas_plano_ui3(app, get_conn, close_conn, Cookie, Request)
        print("Plano: rotas comerciais registradas")
    except Exception as e:
        print(f"Plano rotas comerciais erro: {e}")

    # 4. Registra rotas comerciais, gestao, lab, relatorios
    try:
        import plano_ui3
        plano_ui3.registrar_rotas_plano_ui3(app, get_conn, close_conn, Cookie, Request)
        print("Plano: rotas comerciais registradas")
    except Exception as e:
        print(f"Plano rotas comerciais erro: {e}")