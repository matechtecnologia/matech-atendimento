import os
import google.generativeai as genai
from dotenv import load_dotenv
from prompts import PROMPT_MATECH

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-3.5-flash-lite")

def separar_resposta(texto):
    """Separa a resposta da IA em 4 blocos."""
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
                blocos["acao_crm"] = partes.split("=== LINHA CRM ===")[0].strip()

        if "=== LINHA CRM ===" in texto:
            blocos["linha_crm"] = texto.split("=== LINHA CRM ===")[1].strip()

    except Exception as e:
        blocos["o_que_falar"] = f"ERRO AO SEPARAR: {e}\n\nTexto original:\n{texto}"

    return blocos

def gerar_resposta(linha_crm, mensagem_cliente):
    """Chama a IA e devolve os 4 blocos."""
    prompt_completo = f"""{PROMPT_MATECH}

---

# CONTEXTO DO CLIENTE (linha CRM atual)

{linha_crm}

---

# MENSAGEM DO CLIENTE AGORA

{mensagem_cliente}

---

# SUA TAREFA

Analise o contexto acima + a mensagem do cliente e responda EXATAMENTE no formato obrigatório:

=== O QUE FALAR ===
[áudio de 10-30 segundos]

=== TEXTO PARA ENVIAR ===
[texto curto ou NENHUM]

=== AÇÃO CRM ===
[LEAD / FOLLOW-UP / FECHADO / ONBOARDING]

=== LINHA CRM ===
[linha completa atualizada]
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
            "linha_crm": ""
        }