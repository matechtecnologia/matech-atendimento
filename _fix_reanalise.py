with open("consultor_rotas.py", "r", encoding="utf-8") as f:
    c = f.read()

antigo = '''            _cu.execute("SELECT gargalo_detectado, servico_indicado FROM consultorias WHERE id = %s", (consultoria_id,))
            _r = _cu.fetchone()
            _cu.execute("SELECT COUNT(*) FROM consultoria_passos WHERE consultoria_id = %s", (consultoria_id,))
            _n_passos = _cu.fetchone()[0] or 0
            _cu.close()
            close_conn(_c)
            if _r and _r[0] and _r[1] and _n_passos > 0:
                print(f"Consultor: analise pulada (consultoria #{consultoria_id} ja tem tudo).")
                return'''

novo = '''            _cu.execute("SELECT gargalo_detectado, servico_indicado FROM consultorias WHERE id = %s", (consultoria_id,))
            _r = _cu.fetchone()
            _cu.execute("SELECT COUNT(*) FROM consultoria_passos WHERE consultoria_id = %s", (consultoria_id,))
            _n_passos = _cu.fetchone()[0] or 0
            # Reanalisar a cada 5 mensagens (para atualizar gargalo se mudar)
            _cu.execute("SELECT COUNT(*) FROM consultoria_mensagens WHERE consultoria_id = %s", (consultoria_id,))
            _n_msgs = _cu.fetchone()[0] or 0
            _cu.close()
            close_conn(_c)
            if _r and _r[0] and _r[1] and _n_passos > 0 and _n_msgs % 5 != 0:
                print(f"Consultor: analise pulada (consultoria #{consultoria_id} ja tem tudo, {_n_msgs} msgs).")
                return'''

if antigo in c:
    c = c.replace(antigo, novo)
    with open("consultor_rotas.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - reanalise a cada 5 mensagens")
else:
    print("ERRO - nao achei o bloco")
