import gemini

resultado = gemini.gerar_resposta(
    linha_crm="Nome: Carlos; Produto: Consultoria; Status: Novo Lead",
    mensagem_cliente="Oi, quanto custa?",
    nicho_dict={
        "produto": "Consultoria empresarial",
        "publico": "Donos de PME",
        "preco": "R$ 497",
        "dor": "Falta de organização",
        "objecao": "É caro",
        "diferencial": "Atendimento personalizado",
        "tom": "Direto e consultivo",
    },
)

print("=== RESULTADO ===")
for k, v in resultado.items():
    print(f"{k}: {v[:200]}")
