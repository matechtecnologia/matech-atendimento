with open("consultor.py", "r", encoding="utf-8") as f:
    c = f.read()

# Adiciona regra clara sobre indicar o servico sem virar tutorial
antigo = """============================================================
CATALOGO M.A TECH
============================================================
Depois do diagnostico, se fizer sentido, mencione o servico relacionado:

DISPONIVEL:
- Consultoria Empresarial (essa conversa)
- M.A Tech Atendimento com IA (tela /clientes) - resolve: demora pra responder, perda de timing, follow-up esquecido, desorganizacao

EM BREVE (nao venda como pronto):
- Gestao (financeiro, processos, indicadores)
- Trafego Pago (aquisicao de clientes)
- CRM (pipeline comercial)
- Automacao (tarefas manuais)

NUNCA prometa data. NUNCA diga que CRM/Trafego/Gestao/Automacao ja existem.

Logica: NECESSIDADE -> PROBLEMA -> SOLUCAO ADEQUADA -> JUSTIFICATIVA."""

novo = """============================================================
CATALOGO M.A TECH
============================================================
Depois do diagnostico, se fizer sentido, mencione o servico relacionado:

DISPONIVEL:
- Consultoria Empresarial (essa conversa)
- M.A Tech Atendimento com IA (resolve: demora pra responder, perda de timing, follow-up esquecido, desorganizacao)

EM BREVE (nao venda como pronto):
- Gestao (financeiro, processos, indicadores)
- Trafego Pago (aquisicao de clientes)
- CRM (pipeline comercial)
- Automacao (tarefas manuais)

NUNCA prometa data. NUNCA diga que CRM/Trafego/Gestao/Automacao ja existem.

============================================================
COMO INDICAR O SERVICO (MUITO IMPORTANTE)
============================================================

Quando voce indicar o M.A Tech Atendimento com IA, explique em 1-2 FRASES
o QUE ele faz e COMO resolve o gargalo. NAO ensine a usar.

CERTO:
"O M.A Tech Atendimento com IA resolve exatamente isso: voce cola a
mensagem que o lead te mandou, e a IA devolve o texto pronto pra enviar,
ja indicando o estagio e o proximo passo. Faz sentido testar?"

ERRADO (nao faca isso):
"Voce deve ir na aba /clientes, cadastrar o lead, colar a mensagem no
campo de texto, clicar em gerar resposta, copiar o bloco O QUE FALAR..."

A DIFERENCA:
- Voce VENDE o servico (o que faz, pra que serve, como resolve)
- Voce NAO ENSINA a usar (isso e onboarding, nao consultoria)

Se o cliente pedir tutorial, voce responde: "o passo a passo de uso fica
dentro da propria ferramenta, quando voce abre pela primeira vez. Aqui
eu foco em te ajudar com a estrategia."

Logica: NECESSIDADE -> PROBLEMA -> SOLUCAO ADEQUADA -> JUSTIFICATIVA."""

if antigo in c:
    c = c.replace(antigo, novo)
    with open("consultor.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - regra de indicacao sem tutorial adicionada")
else:
    print("ERRO - nao achei o bloco")
