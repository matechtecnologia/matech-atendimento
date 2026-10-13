with open("app.py", "r", encoding="utf-8") as f:
    c = f.read()

# Modifica processar_atendimento pra carregar campos extras ANTES de gerar resposta
antigo = '''def processar_atendimento(aid, linha_crm, mensagem, prompt, hist, whatsapp, uid, cid=None, nicho_dict=None):
    try:
        r = gerar_resposta(linha_crm, mensagem, prompt, hist, nicho_dict=nicho_dict)'''

novo = '''def processar_atendimento(aid, linha_crm, mensagem, prompt, hist, whatsapp, uid, cid=None, nicho_dict=None):
    try:
        # Carrega campos extras do nicho ANTES de gerar a resposta
        if nicho_dict and nicho_dict.get("id"):
            try:
                _c = get_conn()
                _cu = _c.cursor(cursor_factory=RealDictCursor)
                _cu.execute("SELECT campo, valor FROM nicho_campos_extras WHERE nicho_id = %s", (nicho_dict["id"],))
                _extras = {}
                for _row in _cu.fetchall():
                    _extras[_row["campo"]] = _row["valor"]
                nicho_dict["campos_extras"] = _extras
                _cu.close()
                close_conn(_c)
            except Exception as _e:
                print(f"Erro carregar campos extras: {_e}")

        r = gerar_resposta(linha_crm, mensagem, prompt, hist, nicho_dict=nicho_dict)'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - processar_atendimento atualizado")
else:
    print("ERRO - nao achei o bloco")

# Remove a duplicata que ficou no _rodar_auditoria (agora ja vem carregado)
antigo2 = '''    # Pega campos extras do nicho
    nicho_id = nicho_dict.get("id")
    campos_extras = {}
    if nicho_id:
        cur.execute("SELECT campo, valor FROM nicho_campos_extras WHERE nicho_id = %s", (nicho_id,))
        for row in cur.fetchall():
            campos_extras[row["campo"]] = row["valor"]

    nicho_dict["campos_extras"] = campos_extras
    cur.close()
    close_conn(conn)

    # Roda o auditor'''

novo2 = '''    cur.close()
    close_conn(conn)

    # Roda o auditor'''

if antigo2 in c:
    c = c.replace(antigo2, novo2, 1)
    print("OK - _rodar_auditoria simplificado")
else:
    print("AVISO - bloco auditor nao achado")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - arquivo salvo")
