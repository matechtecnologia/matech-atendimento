with open("gemini.py", "r", encoding="utf-8") as f:
    c = f.read()

antigo = """if IA_ATUAL == "gemini":
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


def _chamar_ia(system_prompt, user_prompt, temperature=0.7, max_tokens=3000):
    \"\"\"Funcao universal: funciona com Groq ou Gemini.\"\"\"
    if IA_ATUAL == "gemini":
        modelo = client.GenerativeModel(
            MODELO,
            system_instruction=system_prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            },
        )
        resp = modelo.generate_content(user_prompt)
        return resp.text
    else:
        r = client.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            timeout=60,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return r.choices[0].message.content"""

novo = """if IA_ATUAL == "gemini":
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    MODELO = "gemini-2.5-flash-lite"
elif IA_ATUAL == "groq":
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    MODELO = "openai/gpt-oss-120b"
else:
    raise Exception(f"IA_ATUAL desconhecido: {IA_ATUAL}")


def _chamar_ia(system_prompt, user_prompt, temperature=0.7, max_tokens=3000):
    \"\"\"Funcao universal: funciona com Groq ou Gemini.\"\"\"
    if IA_ATUAL == "gemini":
        resp = client.models.generate_content(
            model=MODELO,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )
        return resp.text
    else:
        r = client.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            timeout=60,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return r.choices[0].message.content"""

if antigo in c:
    c = c.replace(antigo, novo)
    with open("gemini.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - codigo trocado pro SDK novo")
else:
    print("ERRO - nao achei o bloco")
