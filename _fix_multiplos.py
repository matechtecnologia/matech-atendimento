with open("consultor_core.py", "r", encoding="utf-8") as f:
    c = f.read()

# Troca o bloco de nicho unico por todos os nichos
antigo_nicho = """        cur.execute(\"\"\"
            SELECT nome, produto, publico, preco, dor, objecao, diferencial, tom
            FROM nichos
            WHERE vendedor_id = %s AND COALESCE(ativo, TRUE) = TRUE
            ORDER BY id LIMIT 1
        \"\"\", (vendedor_id,))
        _n = cur.fetchone()
        if _n:
            dossie[\"nicho_detalhado\"] = {
                \"nome\": _n[0] or \"\",
                \"produto\": _n[1] or \"\",
                \"publico\": _n[2] or \"\",
                \"preco\": _n[3] or \"\",
                \"dor\": _n[4] or \"\",
                \"objecao\": _n[5] or \"\",
                \"diferencial\": _n[6] or \"\",
                \"tom\": _n[7] or \"\",
            }
        else:
            dossie[\"nicho_detalhado\"] = None"""

novo_nicho = """        cur.execute(\"\"\"
            SELECT nome, produto, publico, preco, dor, objecao, diferencial, tom
            FROM nichos
            WHERE vendedor_id = %s AND COALESCE(ativo, TRUE) = TRUE
            ORDER BY id
        \"\"\", (vendedor_id,))
        _todos_nichos = []
        for _n in cur.fetchall():
            _todos_nichos.append({
                \"nome\": _n[0] or \"\",
                \"produto\": _n[1] or \"\",
                \"publico\": _n[2] or \"\",
                \"preco\": _n[3] or \"\",
                \"dor\": _n[4] or \"\",
                \"objecao\": _n[5] or \"\",
                \"diferencial\": _n[6] or \"\",
                \"tom\": _n[7] or \"\",
            })
        dossie[\"nichos_detalhados\"] = _todos_nichos
        dossie[\"nicho_detalhado\"] = _todos_nichos[0] if _todos_nichos else None"""

c = c.replace(antigo_nicho, novo_nicho)

# Troca a formatacao de nicho unico por lista de nichos
antigo_format = """    # Nicho detalhado (dados do onboarding)
    nd = dossie.get(\"nicho_detalhado\")
    if nd:
        linhas.append(\"\")
        linhas.append(\"--- NICHO CONFIGURADO (o que ele vende) ---\")
        if nd.get(\"nome\"): linhas.append(f\"Nome do nicho: {nd['nome']}\")
        if nd.get(\"produto\"): linhas.append(f\"O que vende: {nd['produto']}\")
        if nd.get(\"publico\"): linhas.append(f\"Para quem vende: {nd['publico']}\")
        if nd.get(\"preco\"): linhas.append(f\"Preco: {nd['preco']}\")
        if nd.get(\"dor\"): linhas.append(f\"Dor do cliente final: {nd['dor']}\")
        if nd.get(\"objecao\"): linhas.append(f\"Objecao comum: {nd['objecao']}\")
        if nd.get(\"diferencial\"): linhas.append(f\"Diferencial: {nd['diferencial']}\")
        if nd.get(\"tom\"): linhas.append(f\"Tom de voz: {nd['tom']}\")
        linhas.append(\"--- FIM DO NICHO ---\")
    else:
        linhas.append(\"\")
        linhas.append(\"NICHO: ainda nao configurado (o dono nao fez onboarding completo)\")"""

novo_format = """    # Nichos detalhados (todos)
    todos = dossie.get(\"nichos_detalhados\", [])
    if todos:
        linhas.append(\"\")
        linhas.append(f\"--- NICHOS CONFIGURADOS ({len(todos)} cadastrado(s)) ---\")
        for idx, nd in enumerate(todos, 1):
            linhas.append(f\"\")
            linhas.append(f\"NICHO {idx}:\")
            if nd.get(\"nome\"): linhas.append(f\"  Nome: {nd['nome']}\")
            if nd.get(\"produto\"): linhas.append(f\"  O que vende: {nd['produto']}\")
            if nd.get(\"publico\"): linhas.append(f\"  Para quem vende: {nd['publico']}\")
            if nd.get(\"preco\"): linhas.append(f\"  Preco: {nd['preco']}\")
            if nd.get(\"dor\"): linhas.append(f\"  Dor do cliente final: {nd['dor']}\")
            if nd.get(\"objecao\"): linhas.append(f\"  Objecao comum: {nd['objecao']}\")
            if nd.get(\"diferencial\"): linhas.append(f\"  Diferencial: {nd['diferencial']}\")
            if nd.get(\"tom\"): linhas.append(f\"  Tom de voz: {nd['tom']}\")
        linhas.append(\"\")
        linhas.append(\"--- FIM DOS NICHOS ---\")
    else:
        linhas.append(\"\")
        linhas.append(\"NICHO: ainda nao configurado (o dono nao fez onboarding completo)\")"""

c = c.replace(antigo_format, novo_format)

with open("consultor_core.py", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - multiplos nichos")
