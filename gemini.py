import os
import re
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

    # Limpa espaços e normaliza
    texto = texto.strip()

    # Padrões flexíveis (aceita com ou sem ===, maiúsculas/minúsculas)
    padrao_falar = r"={0,3}\s*O QUE FALAR\s*={0,3}"
    padrao_texto = r"={0,3}\s*TEXTO PARA ENVIAR\s*={0,3}"
    padrao_acao = r"={0,3}\s*A[ÇC][ÃA]O CRM\s*={0,3}"
    padrao_crm = r"={0,3}\s*LINHA CRM\s*={0,3}"

    try:
        # Divide por qualquer um dos marcadores, mantendo a ordem
        partes = re.split(f"({padrao_falar}|{padrao_texto}|{padrao_acao}|{padrao_crm})", texto, flags=re.IGNORECASE)

        atual = None
        for i, parte in enumerate(partes):
            parte_limpa = parte.strip()
            if not parte_limpa:
                continue

            if re.match(padrao_falar, parte_limpa, re.IGNORECASE):
                atual = "o_que_falar"
            elif re.match(padrao_texto, parte_limpa, re.IGNORECASE):
                atual = "texto_para_enviar"
            elif re.match(padrao_acao, parte_limpa, re.IGNORECASE):
                atual = "acao_crm"
            elif re.match(padrao_crm, parte_limpa, re.IGNORECASE):
                atual = "linha_crm"
            elif atual:
                # É conteúdo, adiciona no bloco atual
                if blocos[atual]:
                    blocos[atual] += "\n" + parte_limpa
                else:
                    blocos[atual] = parte_limpa

        # Limpa a ação CRM (só a primeira palavra)
        if blocos["acao_crm"]:
            match = re.search(r"(LEAD|FOLLOW-?UP|FECHADO|ONBOARDING)", blocos["acao_crm"], re.IGNORECASE)
            if match:
                blocos["acao_crm"] = match.group(1).upper()

        # Limpa o texto para enviar
        if not blocos["texto_para_enviar"] or blocos["texto_para_enviar"].upper() in ["", "NENHUM", "NENHUM."]:
            blocos["texto_para_enviar"] = "NENHUM"

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

# FORMATO DE RESPOSTA OBRIGATÓRIO

Você DEVE responder EXATAMENTE com os 4 marcadores abaixo, cada um em uma linha sozinha.
NÃO escreva nada fora desses 4 blocos.

=== O QUE FALAR ===
(escreva o roteiro do áudio de 10-30 segundos aqui, nada mais)

=== TEXTO PARA ENVIAR ===
(escreva um texto curto OU a palavra NENHUM)

=== AÇÃO CRM ===
(escreva APENAS uma destas palavras: LEAD ou FOLLOW-UP ou FECHADO ou ONBOARDING)

=== LINHA CRM ===
(Nome: xxx; Nicho: xxx; Objetivo: xxx; Dor: xxx; Objeção: xxx; Estratégia: xxx; Interesse: xxx; Status: xxx; Próximo passo: xxx)
"""

    try:
        response = client.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "system", "content": "Você SEMPRE responde no formato exato solicitado, com os 4 blocos separados. Nunca junta blocos."},
                {"role": "user", "content": prompt_completo}
            ],
            timeout=60,
            temperature=0.7
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

# FORMATO DE RESPOSTA OBRIGATÓRIO

Você DEVE responder EXATAMENTE com os 4 marcadores abaixo, cada um em uma linha sozinha.
NÃO escreva nada fora desses 4 blocos.

=== O QUE FALAR ===
(roteiro do áudio de 10-30 segundos)

=== TEXTO PARA ENVIAR ===
(texto curto OU NENHUM)

=== AÇÃO CRM ===
(APENAS UMA PALAVRA: LEAD ou FOLLOW-UP ou FECHADO ou ONBOARDING)

=== LINHA CRM ===
(Nome: xxx; Nicho: xxx; Objetivo: xxx; Dor: xxx; Objeção: xxx; Estratégia: xxx; Interesse: xxx; Status: xxx; Próximo passo: xxx)
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