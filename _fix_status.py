with open("consultor_rotas.py", "r", encoding="utf-8") as f:
    c = f.read()

antigo = """        try:
            mensagens_pos = _get_mensagens(consultoria_id, get_conn, close_conn)
            historico_pos = formatar_historico(mensagens_pos[-20:])
            _analisar_e_salvar(vendedor_id, consultoria_id, historico_pos, get_conn, close_conn)
        except Exception as e:
            print(f"Consultor: erro no pos-analise - {e}")

        # Se esta respondendo, ele esta vendo - marca como vista
        _marcar_vista(consultoria_id, get_conn, close_conn)

        status = _get_status_completo(vendedor_id, consultoria_id, get_conn, close_conn)"""

novo = """        try:
            mensagens_pos = _get_mensagens(consultoria_id, get_conn, close_conn)
            historico_pos = formatar_historico(mensagens_pos[-20:])
            _analisar_e_salvar(vendedor_id, consultoria_id, historico_pos, get_conn, close_conn)
        except Exception as e:
            print(f"Consultor: erro no pos-analise - {e}")

        # Se esta respondendo, ele esta vendo - marca como vista
        _marcar_vista(consultoria_id, get_conn, close_conn)

        # Status DEPOIS da analise (pra incluir gargalo/servico/passos novos)
        status = _get_status_completo(vendedor_id, consultoria_id, get_conn, close_conn)"""

if antigo in c:
    c = c.replace(antigo, novo)
    with open("consultor_rotas.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - ja estava correto")
else:
    print("ERRO - nao achei")
