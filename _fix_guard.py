# 1. Adiciona guard na rota /consultoria (bloqueia nao-admin)
with open("consultor_rotas.py", "r", encoding="utf-8") as f:
    c = f.read()

antigo = """    @app.get("/consultoria", response_class=HTMLResponse)
    def tela_consultoria(request: Request,
                         usuario_id: str = Cookie(None),
                         usuario_nome: str = Cookie(None)):
        if not usuario_id:
            return RedirectResponse(url="/login")

        vendedor_id = _get_vendedor_id(usuario_id, get_conn, close_conn)"""

novo = """    @app.get("/consultoria", response_class=HTMLResponse)
    def tela_consultoria(request: Request,
                         usuario_id: str = Cookie(None),
                         usuario_nome: str = Cookie(None),
                         usuario_tipo: str = Cookie(None)):
        if not usuario_id:
            return RedirectResponse(url="/login")

        # Cliente comum -> tela em desenvolvimento
        if usuario_tipo != "admin":
            return RedirectResponse(url="/consultoria-premium")

        vendedor_id = _get_vendedor_id(usuario_id, get_conn, close_conn)"""

if antigo in c:
    c = c.replace(antigo, novo)
    with open("consultor_rotas.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - guard admin na rota /consultoria")
else:
    print("ERRO - nao achei o bloco /consultoria")

# 2. Troca o link no hub (e no menu inferior) pra /consultoria-premium
with open("templates/hub.html", "r", encoding="utf-8") as f:
    c2 = f.read()
c2 = c2.replace('href="/consultoria/loading"', 'href="/consultoria-premium"')
with open("templates/hub.html", "w", encoding="utf-8") as f:
    f.write(c2)
print("OK - hub.html aponta pra /consultoria-premium")
