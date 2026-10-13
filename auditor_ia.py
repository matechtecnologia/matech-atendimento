# auditor_ia.py
# IA que audita a resposta gerada e detecta invenções.

import os
import json
from dotenv import load_dotenv

load_dotenv()


PROMPT_AUDITOR = """Voce e o AUDITOR da IA de atendimento da M.A Tech.

Sua funcao: analisar a resposta que a IA acabou de gerar e detectar se ela INVENTOU informacao que nao estava no cadastro do negocio.

============================================================
CONTEXTO
============================================================

O negocio tem um NICHO cadastrado com:
- Produto
- Publico
- Preco
- Dor do cliente
- Objecao comum
- Diferencial
- Tom de voz
- Campos extras (endereco, telefone, horario, etc - se cadastrados)

A IA NAO pode inventar informacao que nao esta nesse cadastro.

============================================================
SUA TAREFA
============================================================

Analise a RESPOSTA da IA e responda:

1. A IA citou alguma informacao especifica que NAO estava no cadastro?
   Exemplos: endereco, telefone, horario de funcionamento, formas de pagamento,
   politica de troca, prazo de entrega, nome do dono, nome da empresa.

2. Se sim, qual campo faltou no cadastro?
   Opcoes: endereco, telefone, horario, formas_pagamento, politica_troca,
           prazo_entrega, nome_dono, nome_empresa, outro

3. O que a IA disse (a informacao inventada)?

4. Qual pergunta fazer pro vendedor pra corrigir?

============================================================
FORMATO DA RESPOSTA
============================================================

Responda APENAS com JSON valido, sem texto extra, sem crase, sem markdown.

Formato exato:
{{"inventou": true ou false, "campo": "endereco", "o_que_a_ia_disse": "...", "pergunta_pro_vendedor": "..."}}

Se NAO inventou nada:
{{"inventou": false, "campo": "", "o_que_a_ia_disse": "", "pergunta_pro_vendedor": ""}}

============================================================
NICHO CADASTRADO
============================================================
{nicho}

============================================================
RESPOSTA DA IA (analise isso)
============================================================
{resposta}

JSON:"""


def auditar_resposta(resposta_ia, nicho_dict):
    """Analisa a resposta da IA e detecta invencao.
    
    Retorna dict:
    {
      "inventou": bool,
      "campo": str,
      "o_que_a_ia_disse": str,
      "pergunta_pro_vendedor": str,
    }
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"inventou": False, "campo": "", "o_que_a_ia_disse": "", "pergunta_pro_vendedor": ""}

    # Monta o nicho
    nicho_txt = f"""Produto: {nicho_dict.get('produto', '')}
Publico: {nicho_dict.get('publico', '')}
Preco: {nicho_dict.get('preco', '')}
Dor: {nicho_dict.get('dor', '')}
Objecao: {nicho_dict.get('objecao', '')}
Diferencial: {nicho_dict.get('diferencial', '')}
Tom: {nicho_dict.get('tom', '')}"""

    # Campos extras
    extras = nicho_dict.get("campos_extras", {})
    if extras:
        nicho_txt += "\n\nCampos extras:\n"
        for k, v in extras.items():
            nicho_txt += f"- {k}: {v}\n"
    else:
        nicho_txt += "\n\nCampos extras: NENHUM cadastrado"

    prompt = PROMPT_AUDITOR.format(nicho=nicho_txt, resposta=resposta_ia)

    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=800,
            ),
        )
        texto = (resp.text or "").strip()

        # Extrai JSON
        import re
        m = re.search(r"\{.*\}", texto, re.DOTALL)
        if not m:
            return {"inventou": False, "campo": "", "o_que_a_ia_disse": "", "pergunta_pro_vendedor": ""}

        dados = json.loads(m.group(0))
        return {
            "inventou": bool(dados.get("inventou", False)),
            "campo": dados.get("campo", ""),
            "o_que_a_ia_disse": dados.get("o_que_a_ia_disse", ""),
            "pergunta_pro_vendedor": dados.get("pergunta_pro_vendedor", ""),
        }
    except Exception as e:
        print(f"Auditor: erro - {e}")
        return {"inventou": False, "campo": "", "o_que_a_ia_disse": "", "pergunta_pro_vendedor": ""}
