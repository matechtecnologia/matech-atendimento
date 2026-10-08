import re

with open("consultor_rotas.py", "r", encoding="utf-8") as f:
    c = f.read()

# Remove do prompt da 2a chamada tudo sobre "COMO O M.A TECH FUNCIONA" e "O QUE NAO EXISTE"
inicio = c.find('prompt = f"""Analise a conversa abaixo')
fim = c.find('CONVERSA:\n{historico_txt}\n\nJSON:"""', inicio)

if inicio != -1 and fim != -1:
    novo_prompt = '''prompt = f"""Analise a conversa abaixo entre um CONSULTOR da M.A Tech e um EMPRESARIO.

Extraia 3 informacoes em formato JSON.

- "gargalo": o problema principal do negocio (frase curta, ate 60 chars)
- "servico": atendimento_ia, gestao, trafego, crm, automacao, ou nenhum
- "passos": lista de 3 a 5 acoes praticas que o EMPRESARIO deve tomar no negocio dele
  Cada passo: "titulo" (ate 40 chars), "acao" (ate 200 chars), "prazo" (hoje/essa semana/esse mes)

Os passos devem ser acoes REAIS de negocio (ex: "Ligar para os 3 leads pendentes", "Definir oferta clara", "Calcular ticket medio"). NUNCA passos sobre usar software ou ferramenta.

Responda APENAS com JSON valido, sem texto extra, sem crase, sem markdown.

Formato exato:
{{"gargalo": "...", "servico": "...", "passos": [{{"titulo": "...", "acao": "...", "prazo": "..."}}]}}

CONVERSA:
{historico_txt}

JSON:"""'''
    
    c = c[:inicio] + novo_prompt + c[fim+len('CONVERSA:\n{historico_txt}\n\nJSON:"""'):]
    
    with open("consultor_rotas.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - prompt da 2a chamada limpo")
else:
    print("ERRO - nao achei o bloco")
