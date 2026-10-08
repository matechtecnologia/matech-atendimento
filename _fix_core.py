with open("consultor_core.py", "r", encoding="utf-8") as f:
    c = f.read()

# Adiciona coleta de nicho detalhado + clientes concretos, DEPOIS de "NICHOS CADASTRADOS"
antigo = """        # -------------------------------------------------------
        # 8. USO DE IA NO MES (respostas_ia)
        # -------------------------------------------------------"""

novo = """        # -------------------------------------------------------
        # 7b. NICHO COMPLETO (com dados do onboarding)
        # -------------------------------------------------------
        cur.execute(\"\"\"
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
            dossie[\"nicho_detalhado\"] = None

        # -------------------------------------------------------
        # 7c. CLIENTES CONCRETOS (nomes + status + tempo sem contato)
        # -------------------------------------------------------
        cur.execute(\"\"\"
            SELECT nome, COALESCE(status, 'novo lead') AS status, criado_em
            FROM clientes
            WHERE vendedor_id = %s
            ORDER BY id DESC LIMIT 10
        \"\"\", (vendedor_id,))
        _cs = []
        for _c in cur.fetchall():
            _cs.append({
                \"nome\": _c[0] or \"(sem nome)\",
                \"status\": _c[1] or \"novo lead\",
                \"criado_em\": _c[2].isoformat() if _c[2] else None,
            })
        dossie[\"clientes_detalhados\"] = _cs

        # -------------------------------------------------------
        # 8. USO DE IA NO MES (respostas_ia)
        # -------------------------------------------------------"""

if antigo in c:
    c = c.replace(antigo, novo)
    with open("consultor_core.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - consultor_core.py com nicho detalhado + clientes concretos")
else:
    print("ERRO - nao achei o bloco")
