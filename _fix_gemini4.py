with open("gemini.py", "r", encoding="utf-8") as f:
    c = f.read()

antigo = '''    try:
        r = client.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "system", "content": prompt_mae},
                {"role": "user", "content": dados},
            ],
            temperature=0.7,
            max_tokens=3000,
            timeout=60,
        )
        texto = r.choices[0].message.content.strip()
        if texto:
            print("[gemini] prompt personalizado gerado para nicho: " + (nome_nicho or "?"))
            return texto
    except Exception as e:
        print("[gemini] erro gerar_prompt_personalizado: " + str(e))'''

novo = '''    try:
        texto = _chamar_ia(prompt_mae, dados, temperature=0.7, max_tokens=3000).strip()
        if texto:
            print("[gemini] prompt personalizado gerado para nicho: " + (nome_nicho or "?"))
            return texto
    except Exception as e:
        print("[gemini] erro gerar_prompt_personalizado: " + str(e))'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    with open("gemini.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - 3a chamada trocada")
else:
    print("ERRO - nao achei")

# Testa sintaxe
import subprocess
result = subprocess.run(["python", "-c", "import gemini; print('Sintaxe OK')"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
