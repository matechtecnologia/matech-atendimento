with open("app.py", "r", encoding="utf-8") as f:
    c = f.read()

antigo = """    # Verifica limite mensal de respostas
    try:
        usadas = contar_respostas_mes(vid_real)
        limite = LIMITES_RESPOSTAS.get(vendedor_atual["plano"], 300)
        if usadas >= limite:
            return RedirectResponse(url="/planos?erro=Limite+de+respostas+atingido.+Faca+upgrade", status_code=303)
    except Exception as _e:
        print("Erro verificar limite:", _e)"""

novo = """    # Verifica limite mensal de respostas (aviso 100%, bloqueio 120%)
    try:
        usadas = contar_respostas_mes(vid_real)
        limite = LIMITES_RESPOSTAS.get(vendedor_atual["plano"], 150)
        # Bloqueia so em 120% (da margem pro cliente continuar)
        if usadas >= int(limite * 1.2):
            return RedirectResponse(url="/planos?erro=Limite+de+respostas+atingido.+Faca+upgrade+ou+compre+extras", status_code=303)
    except Exception as _e:
        print("Erro verificar limite:", _e)"""

if antigo in c:
    c = c.replace(antigo, novo, 1)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - logica de bloqueio atualizada (aviso 100%, bloqueio 120%)")
else:
    print("ERRO - nao achei o bloco")
