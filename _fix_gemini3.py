with open("gemini.py", "r", encoding="utf-8") as f:
    c = f.read()

# Troca 2a chamada (streaming)
antigo2 = '''    try:
        r = client.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "system", "content": "Voce e um closer consultivo. Entende antes de recomendar. Nunca vende no primeiro contato. Nunca repete saudacao se ja conversou. Uma pergunta por vez. Nunca fica em interrogatorio. Nunca usa frases genericas. Responda SEMPRE com os 4 blocos exatos."},
                {"role": "user", "content": prompt}
            ],
            timeout=60,
            temperature=0.7,
            max_tokens=3000,
            stream=True
        )
        for chunk in r:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content'''

novo2 = '''    try:
        system_prompt = "Voce e um closer consultivo. Entende antes de recomendar. Nunca vende no primeiro contato. Nunca repete saudacao se ja conversou. Uma pergunta por vez. Nunca fica em interrogatorio. Nunca usa frases genericas. Responda SEMPRE com os 4 blocos exatos."
        # Gemini nao faz streaming na helper universal - usa normal
        texto = _chamar_ia(system_prompt, prompt, temperature=0.7, max_tokens=3000)
        yield texto'''

if antigo2 in c:
    c = c.replace(antigo2, novo2, 1)
    with open("gemini.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - 2a chamada (streaming) trocada")
else:
    print("ERRO - nao achei 2a chamada")
