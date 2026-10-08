with open("consultor_core.py", "r", encoding="utf-8") as f:
    c = f.read()

antigo = """    linhas.append("=== FIM DO DOSSIE ===")
    return "\\n".join(linhas)"""

novo = """    # Nicho detalhado (dados do onboarding)
    nd = dossie.get("nicho_detalhado")
    if nd:
        linhas.append("")
        linhas.append("--- NICHO CONFIGURADO (o que ele vende) ---")
        if nd.get("nome"): linhas.append(f"Nome do nicho: {nd['nome']}")
        if nd.get("produto"): linhas.append(f"O que vende: {nd['produto']}")
        if nd.get("publico"): linhas.append(f"Para quem vende: {nd['publico']}")
        if nd.get("preco"): linhas.append(f"Preco: {nd['preco']}")
        if nd.get("dor"): linhas.append(f"Dor do cliente final: {nd['dor']}")
        if nd.get("objecao"): linhas.append(f"Objecao comum: {nd['objecao']}")
        if nd.get("diferencial"): linhas.append(f"Diferencial: {nd['diferencial']}")
        if nd.get("tom"): linhas.append(f"Tom de voz: {nd['tom']}")
        linhas.append("--- FIM DO NICHO ---")
    else:
        linhas.append("")
        linhas.append("NICHO: ainda nao configurado (o dono nao fez onboarding completo)")

    # Clientes concretos
    cd = dossie.get("clientes_detalhados", [])
    if cd:
        linhas.append("")
        linhas.append("--- ULTIMOS CLIENTES CADASTRADOS ---")
        for cli in cd[:10]:
            linhas.append(f"- {cli['nome']} (status: {cli['status']})")
        linhas.append("--- FIM DOS CLIENTES ---")

    linhas.append("=== FIM DO DOSSIE ===")
    return "\\n".join(linhas)"""

if antigo in c:
    c = c.replace(antigo, novo)
    with open("consultor_core.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - formatacao com nicho e clientes")
else:
    print("ERRO - nao achei o bloco")
