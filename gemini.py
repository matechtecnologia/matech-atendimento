import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("Chave da Groq nao encontrada! Configure GROQ_API_KEY.")

client = Groq(api_key=api_key)

MODELO = "openai/gpt-oss-120b"

def separar_resposta(texto):
    blocos = {
        "o_que_falar": "",
        "texto_para_enviar": "NENHUM",
        "acao_crm": "LEAD",
        "linha_crm": ""
    }

    try:
        if "=== O QUE FALAR ===" in texto:
            partes = texto.split("=== O QUE FALAR ===")[1]
            if "=== TEXTO PARA ENVIAR ===" in partes:
                blocos["o_que_falar"] = partes.split("=== TEXTO PARA ENVIAR ===")[0].strip()

        if "=== TEXTO PARA ENVIAR ===" in texto:
            partes = texto.split("=== TEXTO PARA ENVIAR ===")[1]
            if "=== AÇÃO CRM ===" in partes:
                blocos["texto_para_enviar"] = partes.split("=== AÇÃO CRM ===")[0].strip()

        if "=== AÇÃO CRM ===" in texto:
            partes = texto.split("=== AÇÃO CRM ===")[1]
            if "=== LINHA CRM ===" in partes:
                blocos["acao_crm"] = partes.split("=== AÇÃO CRM ===")[0].strip()

        if "=== LINHA CRM ===" in texto:
            blocos["linha_crm"] = texto.split("=== LINHA CRM ===")[1].strip()

    except Exception as e:
        blocos["o_que_falar"] = f"ERRO AO SEPARAR: {e}\n\nTexto original:\n{texto}"

    return blocos


def gerar_resposta(linha_crm, mensagem_cliente, prompt_vendedor=None, historico=""):
    if not prompt_vendedor:
        prompt_vendedor = "Você é um closer estratégico."

    prompt_completo = f"""{prompt_vendedor}

---

# CONTEXTO DO CLIENTE (CRM)

{linha_crm}

---

# HISTÓRICO RECENTE DA CONVERSA

{historico if historico else "Primeira interação com este cliente."}

---

# MENSAGEM ATUAL

{mensagem_cliente}

---

# SUA TAREFA

Responda EXATAMENTE neste formato:

=== O QUE FALAR ===
[áudio de 10-30 segundos]

=== TEXTO PARA ENVIAR ===
[texto curto ou NENHUM]

=== AÇÃO CRM ===
[LEAD / FOLLOW-UP / FECHADO / ONBOARDING]

=== LINHA CRM ===
[Nome: xxx; Nicho: xxx; Objetivo: xxx; Dor: xxx; Objeção: xxx; Estratégia: xxx; Interesse: xxx; Status: xxx; Próximo passo: xxx]
"""

    try:
        response = client.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "user", "content": prompt_completo}
            ],
            timeout=60
        )
        texto = response.choices[0].message.content
        return separar_resposta(texto)
    except Exception as e:
        return {
            "o_que_falar": f"ERRO NA API: {e}",
            "texto_para_enviar": "NENHUM",
            "acao_crm": "ERRO",
            "linha_crm": ""
        }


def gerar_prompt_vendedor(produto, publico, preco, dor, objecao, diferencial, tom):
    prompt_base = """Você é um closer estratégico especializado em vendas consultivas.

---

# SOBRE O PRODUTO/SERVIÇO

{produto}

---

# PÚBLICO-ALVO

{publico}

---

# PREÇO

{preco}

---

# DOR PRINCIPAL DO CLIENTE

{dor}

---

# OBJEÇÕES MAIS COMUNS

{objecao}

---

# DIFERENCIAL

{diferencial}

---

# TOM DE VOZ

{tom}

---

# REGRAS CRÍTICAS DE ATENDIMENTO

1. NUNCA faça mais de uma pergunta por vez
2. NUNCA pergunte o óbvio
3. Use todo o contexto acumulado (CRM + histórico)
4. Cada mensagem deve mover a venda para frente
5. Áudios de 10-30 segundos, linguagem natural
6. Texto apenas quando for preço, link, endereço ou informação técnica

---

# REGRA ESPECIAL — INSTRUÇÃO DO VENDEDOR

O campo "MENSAGEM DO CLIENTE AGORA" pode conter duas coisas:

A) A FALA DO CLIENTE (ex: "quanto custa?", "vou pensar")
   → Responda normalmente ao cliente

B) UMA INSTRUÇÃO DO VENDEDOR (ex: "fazer prospecção fria")
   → NÃO responda como se fosse o cliente
   → GERE a mensagem que o vendedor pediu

---

# FORMATO OBRIGATÓRIO DE RESPOSTA

Sempre responda EXATAMENTE neste formato:

=== O QUE FALAR ===
[áudio de 10-30 segundos]

=== TEXTO PARA ENVIAR ===
[texto curto ou NENHUM]

=== AÇÃO CRM ===
[LEAD / FOLLOW-UP / FECHADO / ONBOARDING]

=== LINHA CRM ===
[Nome: xxx; Nicho: xxx; Objetivo: xxx; Dor: xxx; Objeção: xxx; Estratégia: xxx; Interesse: xxx; Status: xxx; Próximo passo: xxx]
"""
    return prompt_base.format(
        produto=produto,
        publico=publico,
        preco=preco,
        dor=dor,
        objecao=objecao,
        diferencial=diferencial,
        tom=tom
    )