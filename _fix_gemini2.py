with open("gemini.py", "r", encoding="utf-8") as f:
    c = f.read()

# Adiciona funcao helper depois do bloco de config (linha 25 aproximadamente)
antigo_config = 'else:\n    raise Exception(f"IA_ATUAL desconhecido: {IA_ATUAL}")'

novo_config = '''else:
    raise Exception(f"IA_ATUAL desconhecido: {IA_ATUAL}")


def _chamar_ia(system_prompt, user_prompt, temperature=0.7, max_tokens=3000):
    """Funcao universal: funciona com Groq ou Gemini."""
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
        return r.choices[0].message.content'''

if antigo_config in c:
    c = c.replace(antigo_config, novo_config, 1)
    print("OK - funcao helper criada")
else:
    print("ERRO - nao achei bloco de config")

# Troca as 3 chamadas. Primeiro bloco (linha ~339)
antigo1 = '''    try:
        r = client.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "system", "content": "Voce e um closer consultivo. Entende antes de recomendar. Nunca vende no primeiro contato. Nunca repete saudacao se ja conversou. Uma pergunta por vez. Nunca fica em interrogatorio. Se receber INSTRUCAO DIRETA DO VENDEDOR, executa direto sem responder 'claro'. Nunca usa frases genericas. Responda SEMPRE com os 4 blocos exatos."},
                {"role": "user", "content": prompt}
            ],
            timeout=60,
            temperature=0.7,
            max_tokens=3000
        )
        return separar_resposta(r.choices[0].message.content)
    except Exception as e:
        return {"o_que_falar": "ERRO NA API: " + str(e), "texto_para_enviar": "NENHUM", "estagio": "Em Atendimento", "linha_crm": ""}'''

novo1 = '''    try:
        system_prompt = "Voce e um closer consultivo. Entende antes de recomendar. Nunca vende no primeiro contato. Nunca repete saudacao se ja conversou. Uma pergunta por vez. Nunca fica em interrogatorio. Se receber INSTRUCAO DIRETA DO VENDEDOR, executa direto sem responder 'claro'. Nunca usa frases genericas. Responda SEMPRE com os 4 blocos exatos."
        resposta_texto = _chamar_ia(system_prompt, prompt, temperature=0.7, max_tokens=3000)
        return separar_resposta(resposta_texto)
    except Exception as e:
        return {"o_que_falar": "ERRO NA API: " + str(e), "texto_para_enviar": "NENHUM", "estagio": "Em Atendimento", "linha_crm": ""}'''

if antigo1 in c:
    c = c.replace(antigo1, novo1, 1)
    print("OK - 1a chamada trocada")
else:
    print("AVISO - 1a chamada nao achei (pode ter variacao)")

with open("gemini.py", "w", encoding="utf-8") as f:
    f.write(c)
