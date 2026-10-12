with open("gemini.py", "r", encoding="utf-8") as f:
    c = f.read()

# Troca o bloco de configuracao
antigo = """import os
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ============================================================
# CONFIGURACAO DA IA
# Troque aqui quando mudar de provedor:
#   "groq"   - atual (usa GROQ_API_KEY)
#   "gemini" - usa GEMINI_API_KEY
#   "openai" - usa OPENAI_API_KEY
# ============================================================
IA_ATUAL = "groq"

if IA_ATUAL == "groq":
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    MODELO = "openai/gpt-oss-120b"
else:
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    MODELO = "openai/gpt-oss-120b"
"""

novo = """import os
import re
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURACAO DA IA
# Troque aqui quando mudar de provedor:
#   "groq"   - usa GROQ_API_KEY
#   "gemini" - usa GEMINI_API_KEY
# ============================================================
IA_ATUAL = "gemini"

if IA_ATUAL == "gemini":
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    client = genai
    MODELO = "gemini-2.5-flash-lite"
elif IA_ATUAL == "groq":
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    MODELO = "openai/gpt-oss-120b"
else:
    raise Exception(f"IA_ATUAL desconhecido: {IA_ATUAL}")
"""

if antigo in c:
    c = c.replace(antigo, novo)
    with open("gemini.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - cabecalho trocado para Gemini")
else:
    print("ERRO - nao achei o bloco")
