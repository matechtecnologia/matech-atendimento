with open("gemini.py", "r", encoding="utf-8") as f:
    c = f.read()

# 1. Modifica _montar_prompt pra aceitar campos_extras
antigo = '''def _montar_prompt(linha_crm, mensagem_cliente, prompt_vendedor, historico):
    bloco_saud = _bloco_saudacao(historico, mensagem_cliente)
    logica = LOGICA_UNIVERSAL.replace("{bloco_saudacao}", bloco_saud)

    tem_hist = bool(historico and historico.strip() and "Primeira interacao" not in historico)
    hist_txt = historico if tem_hist else "(primeira interacao)"
    crm_txt = linha_crm if linha_crm else "(cliente novo, sem dados)"

    return (
        logica + "\\n\\n"
        "==================================================\\n"
        "CONTEXTO DO NEGOCIO (o que voce vende)\\n"
        "==================================================\\n\\n"
        + (prompt_vendedor or "Produto ou servico generico.") + "\\n\\n"'''

novo = '''def _montar_prompt(linha_crm, mensagem_cliente, prompt_vendedor, historico, campos_extras=None):
    bloco_saud = _bloco_saudacao(historico, mensagem_cliente)
    logica = LOGICA_UNIVERSAL.replace("{bloco_saudacao}", bloco_saud)

    tem_hist = bool(historico and historico.strip() and "Primeira interacao" not in historico)
    hist_txt = historico if tem_hist else "(primeira interacao)"
    crm_txt = linha_crm if linha_crm else "(cliente novo, sem dados)"

    # Campos extras do nicho (endereco, telefone, horario, etc)
    extras_txt = ""
    if campos_extras:
        extras_txt = "\\n\\n==================================================\\n"
        extras_txt += "INFORMACOES EXTRAS DO NEGOCIO\\n"
        extras_txt += "==================================================\\n\\n"
        for k, v in campos_extras.items():
            extras_txt += f"{k.upper()}: {v}\\n"

    return (
        logica + "\\n\\n"
        "==================================================\\n"
        "CONTEXTO DO NEGOCIO (o que voce vende)\\n"
        "==================================================\\n\\n"
        + (prompt_vendedor or "Produto ou servico generico.") + extras_txt + "\\n\\n"'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    print("OK - _montar_prompt atualizado")
else:
    print("AVISO - bloco _montar_prompt nao encontrado")

# 2. Passa campos_extras pra _montar_prompt em gerar_resposta
antigo2 = '''    prompt = _montar_prompt(linha_crm, mensagem_cliente, prompt_vendedor, historico)'''
novo2 = '''    campos_extras = None
    if nicho_dict:
        campos_extras = nicho_dict.get("campos_extras")
    prompt = _montar_prompt(linha_crm, mensagem_cliente, prompt_vendedor, historico, campos_extras=campos_extras)'''

count = c.count(antigo2)
c = c.replace(antigo2, novo2)
print(f"OK - {count} chamadas de _montar_prompt atualizadas")

with open("gemini.py", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - arquivo salvo")
