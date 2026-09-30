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

ESTAGIOS_VALIDOS = ["Novo Lead", "Em Atendimento", "Negociação", "Cliente", "Perdido"]


def _normalizar_estagio(txt):
    txt = txt.strip().lower()
    if "novo" in txt or "lead" in txt:
        return "Novo Lead"
    if "negocia" in txt or "propos" in txt or "interessad" in txt:
        return "Negociação"
    if "fech" in txt or "cliente" in txt or "onboard" in txt or "vend" in txt or "compr" in txt:
        return "Cliente"
    if "perdid" in txt or "desist" in txt:
        return "Perdido"
    if "atend" in txt or "follow" in txt:
        return "Em Atendimento"
    return "Em Atendimento"


def separar_resposta(texto):
    blocos = {
        "o_que_falar": "",
        "texto_para_enviar": "NENHUM",
        "estagio": "Em Atendimento",
        "linha_crm": ""
    }

    texto = texto.strip()

    padrao_falar = r"={0,3}\s*O QUE FALAR\s*={0,3}"
    padrao_texto = r"={0,3}\s*TEXTO PARA ENVIAR\s*={0,3}"
    padrao_estagio = r"={0,3}\s*(?:EST[ÁA]GIO|A[ÇC][ÃA]O CRM|STAGE)\s*={0,3}"
    padrao_crm = r"={0,3}\s*LINHA CRM\s*={0,3}"

    try:
        partes = re.split(
            f"({padrao_falar}|{padrao_texto}|{padrao_estagio}|{padrao_crm})",
            texto,
            flags=re.IGNORECASE
        )

        atual = None
        for parte in partes:
            parte_limpa = parte.strip()
            if not parte_limpa:
                continue

            if re.match(padrao_falar, parte_limpa, re.IGNORECASE):
                atual = "o_que_falar"
            elif re.match(padrao_texto, parte_limpa, re.IGNORECASE):
                atual = "texto_para_enviar"
            elif re.match(padrao_estagio, parte_limpa, re.IGNORECASE):
                atual = "estagio"
            elif re.match(padrao_crm, parte_limpa, re.IGNORECASE):
                atual = "linha_crm"
            elif atual:
                if blocos[atual]:
                    blocos[atual] += "\n" + parte_limpa
                else:
                    blocos[atual] = parte_limpa

        # Normaliza estágio
        blocos["estagio"] = _normalizar_estagio(blocos["estagio"])

        # Limpa texto
        if not blocos["texto_para_enviar"] or blocos["texto_para_enviar"].upper().strip(".") in ["", "NENHUM"]:
            blocos["texto_para_enviar"] = "NENHUM"

    except Exception as e:
        blocos["o_que_falar"] = f"ERRO AO SEPARAR: {e}\n\nTexto original:\n{texto}"

    return blocos


def gerar_resposta(linha_crm, mensagem_cliente, prompt_vendedor=None, historico=""):
    if not prompt_vendedor:
        prompt_vendedor = "Você é um closer estratégico."

    prompt_completo = f"""{prompt_vendedor}

---

# CONTEXTO DO CLIENTE (CRM interno — nunca mostrar ao vendedor)

{linha_crm}

---

# HISTÓRICO RECENTE DA CONVERSA

{historico if historico else "Primeira interação com este cliente."}

---

# MENSAGEM ATUAL

{mensagem_cliente}

---

# FORMATO DE RESPOSTA OBRIGATÓRIO

Responda EXATAMENTE com os 4 marcadores abaixo, cada um em uma linha sozinha.
Nada fora dos blocos.

=== O QUE FALAR ===
(roteiro do áudio de 10-30 segundos, natural, sem jargão)

=== TEXTO PARA ENVIAR ===
(texto curto OU a palavra NENHUM)

=== ESTAGIO ===
(Escolha APENAS UM destes: Novo Lead, Em Atendimento, Negociação, Cliente, Perdido)

=== LINHA CRM ===
(Nome: xxx; Nicho: xxx; Objetivo: xxx; Dor: xxx; Objeção: xxx; Estratégia: xxx; Interesse: xxx; Status: xxx; Próximo passo: xxx)

---

# REGRAS DO ESTÁGIO
- Novo Lead: primeiro contato, ainda sem contexto
- Em Atendimento: já conversou, ainda descobrindo necessidades
- Negociação: demonstrou interesse real, falando de proposta/preço
- Cliente: fechou, comprou, aceitou participar
- Perdido: disse não, desistiu, sem interesse
"""

    try:
        response = client.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "system", "content": "Você responde SEMPRE no formato exato com 4 blocos. Nunca junta blocos."},
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
            "estagio": "Em Atendimento",
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

# REGRAS CRÍTICAS

1. NUNCA faça mais de uma pergunta por vez
2. NUNCA pergunte o óbvio
3. Use todo o contexto acumulado
4. Cada mensagem deve mover a venda para frente
5. Áudios de 10-30 segundos, linguagem natural
6. Texto apenas quando for preço, link, endereço ou informação técnica

---

# REGRA ESPECIAL

O campo "MENSAGEM DO CLIENTE AGORA" pode conter:
A) FALA DO CLIENTE → responda normalmente
B) INSTRUÇÃO DO VENDEDOR (ex: "fazer prospecção fria") → NÃO responda como cliente, GERE a mensagem pedida

---

# FORMATO DE RESPOSTA OBRIGATÓRIO

Responda EXATAMENTE com os 4 marcadores abaixo, cada um em uma linha sozinha.

=== O QUE FALAR ===
(roteiro do áudio de 10-30 segundos)

=== TEXTO PARA ENVIAR ===
(texto curto OU NENHUM)

=== ESTAGIO ===
(Novo Lead, Em Atendimento, Negociação, Cliente ou Perdido)

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


def validar_nicho_ia(nome, produto):
    """Usa IA pra validar se o nicho representa UM produto/servico unico."""
    import json
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = f"""Voce e um validador de nichos de venda. Analise o nicho abaixo.

Nome do nicho: "{nome}"
O que vende: "{produto[:500]}"

REGRAS:
1. Deve representar UM produto/servico especifico
2. NAO pode misturar varios (ex: "carro e moto", "pizza e hamburguer", "curso e mentoria")
3. NAO pode ser vago ("coisas", "produtos", "tudo", "servicos gerais")
4. Uma categoria unica e OK ("pizza", "carro", "consorcio", "consultoria")
5. Abrangente dentro de UMA categoria OK ("lanche", "bebidas"), mas misturando categorias NAO

Responda APENAS nesse JSON (sem markdown, sem explicacao extra):
{{"valido": true, "motivo": "ok"}}
ou
{{"valido": false, "motivo": "explicacao curta"}}
"""
        r = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=150,
        )
        texto = r.choices[0].message.content.strip()
        texto = texto.replace("```json", "").replace("```", "").strip()
        dados = json.loads(texto)
        return dados.get("valido", True), dados.get("motivo", "")
    except Exception as e:
        print(f"Erro validar_nicho_ia: {e}")
        return True, ""
