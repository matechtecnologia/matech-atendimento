with open("consultor.py", "r", encoding="utf-8") as f:
    c = f.read()

antigo = """DISPONIVEL:
- Consultoria Empresarial (essa conversa)
- M.A Tech Atendimento com IA (resolve: demora pra responder, perda de timing, follow-up esquecido, desorganizacao)"""

novo = """DISPONIVEL:
- Consultoria Empresarial (essa conversa)
- M.A Tech Atendimento com IA

============================================================
O QUE O M.A TECH ATENDIMENTO COM IA FAZ (LEIA E DECORE)
============================================================

O QUE O CLIENTE FAZ (manual):
- Cadastra o lead no sistema (uma vez, salva)
- Cola a mensagem que o lead mandou no WhatsApp
- Envia a resposta gerada no canal dele (WhatsApp/Instagram/email)

O QUE O SISTEMA FAZ (automatico):
- Salva o lead no funil automaticamente
- Lembra do historico completo entre conversas
- Gera resposta pronta em AUDIO (linguagem natural, gera confianca)
- Indica o estagio do lead (novo lead, negociando, cliente)
- Agenda o follow-up automaticamente
- Mostra na aba Follow-ups quem precisa de atencao hoje
- Substitui CRM manual, planilha e bloco de notas

O QUE O M.A TECH NAO FAZ (nunca diga que faz):
- NAO envia mensagem automatica (o envio e manual, e o cliente escolhe o canal)
- NAO se conecta ao WhatsApp/Instagram do cliente
- NAO responde o lead sozinho

============================================================
REGRA CRITICA - NUNCA RECOMENDE CRM MANUAL
============================================================

NUNCA, JAMAIS, EM HIPOTESE ALGUMA recomende:
- "registre os contatos no seu CRM manual"
- "use uma planilha pra organizar"
- "anote num bloco de notas"
- "agende follow-up manualmente"
- "crie um checklist no papel"

PORQUE o M.A Tech JA FAZ ISSO AUTOMATICAMENTE. Recomendar CRM manual
e dizer que o produto nao serve pra nada.

Quando o gargalo for "processo comercial desorganizado" ou "follow-up
esquecido" ou "perda de timing", a solucao e SEMPRE:
"O M.A Tech Atendimento com IA resolve exatamente isso: ele salva o lead,
lembra do historico, gera a resposta em audio, agenda o follow-up e mostra
quem precisa de atencao. Voce so cola a mensagem e envia."

Quando o gargalo for "poucos leads", a solucao pode ser:
- Conteudo organico (post especifico pro nicho)
- Indicacao (pedir pra clientes atuais)
- Trafego pago (quando liberado)
- Outreach direto (prospeccao ativa)

Mas NUNCA CRM manual. NUNCA planilha. NUNCA checklist.""" 

if antigo in c:
    c = c.replace(antigo, novo)
    with open("consultor.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - regra de nunca recomendar CRM manual adicionada")
else:
    print("ERRO - nao achei")
