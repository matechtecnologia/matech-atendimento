import os
import google.generativeai as genai
from dotenv import load_dotenv
from prompts import PROMPT_MATECH

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-3.5-flash-lite")

def separar_resposta(texto):
    blocos = {
        "o_que_falar": "",
        "texto_para_enviar": "NENHUM",
        "acao_crm": "LEAD",
        "linha_crm": "",
        "resumo_conversa": ""
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
                blocos["acao_crm"] = partes.split("=== LINHA CRM ===")[0].strip()

        if "=== LINHA CRM ===" in texto:
            partes = texto.split("=== LINHA CRM ===")[1]
            if "=== RESUMO DA CONVERSA ===" in partes:
                blocos["linha_crm"] = partes.split("=== RESUMO DA CONVERSA ===")[0].strip()
            else:
                blocos["linha_crm"] = partes.strip()

        if "=== RESUMO DA CONVERSA ===" in texto:
            blocos["resumo_conversa"] = texto.split("=== RESUMO DA CONVERSA ===")[1].strip()

    except Exception as e:
        blocos["o_que_falar"] = f"ERRO AO SEPARAR: {e}\n\nTexto original:\n{texto}"

    return blocos

def gerar_resposta(linha_crm, mensagem_cliente, prompt_vendedor=None, historico=""):
    if not prompt_vendedor:
        prompt_vendedor = PROMPT_MATECH

    prompt_completo = f"""{prompt_vendedor}

---

# CONTEXTO DO CLIENTE (estado atual — CRM)

{linha_crm}

---

# HISTÓRICO RECENTE DA CONVERSA (memória)

{historico if historico else "Primeira interação com este cliente."}

---

# MENSAGEM ATUAL

{mensagem_cliente}

---

# INSTRUÇÕES SOBRE CRM E HISTÓRICO

CRM = estado ATUAL do cliente (nicho, dor, status, próximo passo)
HISTÓRICO = o que foi DITO na conversa (memória)

REGRA:
- Não duplique informação entre CRM e HISTÓRICO
- O CRM tem o estado. O histórico tem o que foi falado.
- Se algo já está no CRM, não precisa repetir no histórico.

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

=== RESUMO DA CONVERSA ===
[resumo ABREVIADO de tudo que foi dito até agora — máximo 5 linhas — sem duplicar o CRM]
"""

    try:
        resposta = model.generate_content(prompt_completo)
        texto = resposta.text
        return separar_resposta(texto)
    except Exception as e:
        return {
            "o_que_falar": f"ERRO NA API: {e}",
            "texto_para_enviar": "NENHUM",
            "acao_crm": "ERRO",
            "linha_crm": "",
            "resumo_conversa": ""
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

# REGRAS CRÍTICAS

1. NUNCA faça mais de uma pergunta por vez
2. NUNCA pergunte o óbvio
3. Use todo o contexto acumulado (CRM + histórico)
4. Cada mensagem deve mover a venda para frente
5. Áudios de 10-30 segundos
6. Texto apenas quando for preço, link ou informação técnica

---

# REGRA ESPECIAL — INSTRUÇÃO DO VENDEDOR

Se a mensagem começar com "[INSTRUÇÃO DO VENDEDOR":
- NÃO responda como se fosse o cliente
- GERE a mensagem que o vendedor pediu
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