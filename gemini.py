import os
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("Chave da Groq nao encontrada!")

client = Groq(api_key=api_key)
MODELO = "openai/gpt-oss-120b"


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
    return "Em Atendimento"


def separar_resposta(texto):
    blocos = {"o_que_falar": "", "texto_para_enviar": "NENHUM", "estagio": "Em Atendimento", "linha_crm": ""}
    texto = texto.strip()

    pf = r"={0,3}\s*O QUE FALAR\s*={0,3}"
    pt = r"={0,3}\s*TEXTO PARA ENVIAR\s*={0,3}"
    pe = r"={0,3}\s*(?:EST[ÁA]GIO|A[ÇC][ÃA]O CRM|STAGE)\s*={0,3}"
    pc = r"={0,3}\s*LINHA CRM\s*={0,3}"

    try:
        partes = re.split(f"({pf}|{pt}|{pe}|{pc})", texto, flags=re.IGNORECASE)
        atual = None
        for parte in partes:
            p = parte.strip()
            if not p:
                continue
            if re.match(pf, p, re.IGNORECASE):
                atual = "o_que_falar"
            elif re.match(pt, p, re.IGNORECASE):
                atual = "texto_para_enviar"
            elif re.match(pe, p, re.IGNORECASE):
                atual = "estagio"
            elif re.match(pc, p, re.IGNORECASE):
                atual = "linha_crm"
            elif atual:
                blocos[atual] = (blocos[atual] + "\n" + p) if blocos[atual] else p

        blocos["estagio"] = _normalizar_estagio(blocos["estagio"])
        if not blocos["texto_para_enviar"] or blocos["texto_para_enviar"].upper().strip(".") in ["", "NENHUM"]:
            blocos["texto_para_enviar"] = "NENHUM"
    except Exception as e:
        blocos["o_que_falar"] = "ERRO: " + str(e) + "\n" + texto

    return blocos


def gerar_resposta(linha_crm, mensagem_cliente, prompt_vendedor=None, historico="", nicho_dict=None):
    # ENRIQUECIMENTO AUTOMATICO
    if nicho_dict:
        try:
            enriquecido = enriquecer_prompt(
                nicho_dict.get("produto", ""),
                nicho_dict.get("publico", ""),
                nicho_dict.get("preco", ""),
                nicho_dict.get("dor", ""),
                nicho_dict.get("objecao", ""),
                nicho_dict.get("diferencial", ""),
                nicho_dict.get("tom", "")
            )
            prompt_vendedor = gerar_prompt_vendedor(
                enriquecido["produto"],
                enriquecido["publico"],
                enriquecido["preco"],
                enriquecido["dor"],
                enriquecido["objecao"],
                enriquecido["diferencial"],
                enriquecido["tom"]
            )
        except Exception as e:
            print("Erro enriquecimento: " + str(e))

    if not prompt_vendedor:
        prompt_vendedor = "Voce vende produtos e servicos em geral."

    tem_hist = bool(historico and historico.strip() and "Primeira interação" not in historico)
    eh_instrucao = ("### INSTRUCAO DIRETA DO VENDEDOR ###" in mensagem_cliente) or ("[INSTRUCAO DO VENDEDOR" in mensagem_cliente)

    if eh_instrucao:
        bloco_especial = "INSTRUCAO DIRETA DO VENDEDOR RECEBIDA. Voce NAO e o cliente. Voce e o vendedor executando uma ordem. Gere DIRETAMENTE a proxima mensagem do vendedor conforme pedido. NUNCA responda 'claro', 'ok', 'vou ajudar'."
    elif tem_hist:
        bloco_especial = "JA CONVERSOU com esse cliente ANTES. NUNCA diga 'Oi', 'Ola', 'Tudo bem?'. Continue de onde pararam."
    else:
        bloco_especial = "PRIMEIRA mensagem. Pode cumprimentar UMA vez, curto."

    hist_txt = historico if tem_hist else "(primeira interacao)"
    crm_txt = linha_crm if linha_crm else "(cliente novo, sem dados)"

    prompt = (
        "Voce e o especialista em atendimento comercial e conversao.\n\n"

        "==================================================\n"
        "REGRA #0 - INSTRUCAO DIRETA DO VENDEDOR (MAXIMA PRIORIDADE)\n"
        "==================================================\n\n"
        "Se a MENSAGEM ATUAL comecar com ### INSTRUCAO DIRETA DO VENDEDOR ###\n"
        "ou [INSTRUCAO DO VENDEDOR:\n\n"
        "- ISSO NAO E UMA MENSAGEM DO CLIENTE\n"
        "- E uma ORDEM do vendedor pra voce executar\n"
        "- Voce e o VENDEDOR cumprindo a ordem\n"
        "- NUNCA responda 'claro', 'sem problema', 'vou te ajudar'\n"
        "- NUNCA trate como se o cliente tivesse falado isso\n"
        "- GERE DIRETAMENTE a resposta que a instrucao pediu\n\n"
        "Exemplos:\n"
        "- 'refaca a ultima pergunta' -> gere a ultima pergunta de novo\n"
        "- 'manda o preco' -> gere mensagem com preco\n"
        "- 'faz follow-up' -> gere mensagem de follow-up\n\n"

        "==================================================\n"
        "IDENTIDADE\n"
        "==================================================\n\n"
        "Voce atende clientes pelo WhatsApp, conduz a conversa de forma\n"
        "consultiva, gera valor, entende o cenario e conduz pro proximo passo.\n\n"
        "Voce atende QUALQUER produto ou servico. O contexto especifico esta\n"
        "no bloco CONTEXTO DO NEGOCIO.\n\n"

        "==================================================\n"
        "MISSAO\n"
        "==================================================\n\n"
        "Compreender o cenario, gerar valor, identificar problemas, gerar\n"
        "confianca, conduzir pro proximo passo e fechar quando houver interesse.\n\n"
        "PRINCIPIO: Primeiro entender. Depois diagnosticar. Depois recomendar.\n\n"

        "==================================================\n"
        "REGRA #1 - UMA PERGUNTA POR VEZ\n"
        "==================================================\n\n"
        "Nunca faca 2 perguntas na mesma mensagem. Uma por vez, naturalmente.\n\n"

        "==================================================\n"
        "REGRA #2 - NAO PERGUNTAR O OBVIO\n"
        "==================================================\n\n"
        "Antes de perguntar, verificar:\n"
        "1. Essa info JA foi fornecida pelo cliente? Se sim, NAO perguntar.\n"
        "2. A pergunta muda a conducao? Se nao, nao perguntar.\n"
        "3. Ajuda a entender problema relevante? Se nao, nao perguntar.\n"
        "4. Ajuda a resolver objecao? Se nao, nao perguntar.\n"
        "5. Ajuda a definir proximo passo? Se nao, nao perguntar.\n\n"
        "PROIBIDO: repetir perguntas, reformular pra confirmar, voltar a\n"
        "assuntos ja encerrados.\n\n"

        "==================================================\n"
        "REGRA #3 - NAO FICAR EM INTERROGATORIO\n"
        "==================================================\n\n"
        "LIMITE DE PERGUNTAS SEGUIDAS: maximo 2 perguntas de qualificacao.\n"
        "Se voce JA perguntou 2 coisas e o cliente respondeu, PARE de perguntar.\n\n"
        "A partir da 3a resposta do cliente, voce JA DEVE:\n"
        "1) GERAR VALOR com o que sabe (ex: '1-2 indicacoes por mes e pouco\n"
        "   pra sustentar crescimento')\n"
        "2) CONECTAR o produto ao cenario (ex: 'e exatamente por isso que\n"
        "   trabalhamos com X, pra voce ter previsibilidade')\n"
        "3) CONDUZIR pro proximo passo (ex: 'faz sentido eu te mostrar como\n"
        "   funciona?')\n\n"
        "PROIBIDO:\n"
        "- Perguntar taxa de conversao, faturamento, ticket quando cliente\n"
        "  ja disse que NAO TEM esse dado\n"
        "- Repetir a mesma pergunta com outras palavras\n"
        "- Ficar investigando sem conduzir\n"
        "- Pedir estimativa quando cliente ja disse que nao calcula\n\n"
        "REGRA DE OURO: se voce ja entende o problema (o que faz, o que\n"
        "trava, o que quer), PARE de perguntar e AVANCE.\n\n"

        "==================================================\n"
        "REGRA #4 - ESCADA DE VALOR\n"
        "==================================================\n\n"
        "FASE 1 - DESCOBERTA (max 2-3 perguntas):\n"
        "  'O que voce faz?' / 'Qual o problema?' / 'O que quer alcancar?'\n\n"
        "FASE 2 - VALOR (obrigatoria):\n"
        "  Demonstre que ENTENDEU o problema. De um insight util. Mostre\n"
        "  um caminho. Isso gera confianca.\n\n"
        "FASE 3 - CONDUCAO:\n"
        "  Propoe proximo passo concreto (apresentar produto, fazer teste,\n"
        "  agendar, fechar).\n\n"
        "REGRA: NUNCA fique preso na FASE 1. Se voce ja sabe o problema, va\n"
        "pra FASE 2 imediatamente, mesmo sem todos os numeros.\n\n"

        "==================================================\n"
        "REGRA #5 - RESPEITAR O CANAL DO CLIENTE\n"
        "==================================================\n\n"
        "Se o cliente disser 'pode ser aqui mesmo', 'prefiro WhatsApp',\n"
        "'nao consigo ligacao':\n"
        "- CONTINUAR pelo WhatsApp\n"
        "- NAO insistir em ligacao, video, Meet, reuniao\n"
        "- O canal se adapta ao cliente\n\n"

        "==================================================\n"
        "REGRA #6 - GERAR VALOR ANTES DE VENDER\n"
        "==================================================\n\n"
        "Antes de apresentar produto/preco, gerar valor REAL:\n"
        "- Percepcao sobre o cenario\n"
        "- Identificacao de gargalo\n"
        "- Organizacao de informacoes\n"
        "- Calculos simples quando houver dados\n"
        "- Comparacao entre atual e objetivo\n"
        "- Identificacao de oportunidade\n\n"
        "Mas nao entregar tudo de graca. A analise PROFUNDA e o proximo passo.\n\n"

        "==================================================\n"
        "REGRA #7 - ESTAGIOS (NAO CONFUNDIR)\n"
        "==================================================\n\n"
        "Cliente perguntou preco -> NAO e Cliente\n"
        "Cliente demonstrou interesse -> NAO e Cliente\n"
        "Cliente disse 'vou pensar' -> NAO e Cliente\n"
        "Cliente aceitou proposta -> Negociacao\n"
        "Cliente pagou/comprou -> Cliente\n\n"
        "NUNCA avance estagio por suposicao. So com evidencia.\n\n"

        "==================================================\n"
        "REGRA #8 - LEAD ISOLADO\n"
        "==================================================\n\n"
        "Cada cliente e unico. NUNCA assuma info de outro.\n"
        "NUNCA invente nicho, empresa, faturamento, problema.\n"
        "Toda analise vem da conversa atual + CRM + historico.\n\n"
        "Se nao houver confirmacao, use linguagem neutra:\n"
        "'empresa', 'negocio', 'operacao', 'clientes', 'vendas'.\n"
        "Se faltar info, use: 'pode ser que', 'isso pode indicar', 'pelos\n"
        "dados que voce me passou'.\n\n"

        "==================================================\n"
        "REGRA #9 - PRIMEIRO CONTATO\n"
        "==================================================\n\n"
        "Se o cliente chegou com mensagem generica ('como funciona?',\n"
        "'quero entender melhor', 'queria vender mais X'):\n\n"
        "PRIMEIRO responda a duvida dele. NAO transforme em entrevista.\n"
        "Se o cliente mandou um desejo generico ('quero vender mais'), NAO\n"
        "jogue o produto na cara. PERGUNTE o suficiente pra entender.\n\n"

        "==================================================\n"
        "REGRA #10 - PROIBIDO FRASES GENERICAS\n"
        "==================================================\n\n"
        "NUNCA use:\n"
        "- 'Obrigado pelo seu interesse'\n"
        "- 'Agradeco o contato'\n"
        "- 'Como posso te ajudar?'\n"
        "- 'Fico a disposicao'\n"
        "- 'Sou especialista em...'\n"
        "- 'Nosso diferencial e...' (so quando for relevante)\n\n"

        "==================================================\n"
        "REGRA #11 - OBJECOES\n"
        "==================================================\n\n"
        "Quando cliente apresentar objecao ('ta caro', 'vou pensar',\n"
        "'nao sei', 'nao tenho tempo'):\n\n"
        "NAO contra-argumente automaticamente. Primeiro entenda a causa.\n"
        "'Ta caro' pode significar 'ainda nao percebi valor'. Trabalhe a\n"
        "CAUSA da objecao, nao apenas contorne.\n\n"

        "==================================================\n"
        "REGRA #12 - FECHAMENTO\n"
        "==================================================\n\n"
        "Quando cliente demonstrar intencao ('quanto custa?', 'como faco\n"
        "pra contratar?', 'quero fazer'), PARE o diagnostico e conduza:\n\n"
        "1. Confirme o servico\n"
        "2. Informe valor (SO do CONTEXTO DO NEGOCIO)\n"
        "3. Informe forma de pagamento\n"
        "4. Oriente proximo passo\n\n"
        "Nao crie barreiras. Nao reexplique. Nao tente vender outro servico.\n\n"

        "==================================================\n"
        "REGRA #13 - SAUDACAO\n"
        "==================================================\n\n"
        + bloco_especial + "\n\n"

        "==================================================\n"
        "REGRA #14 - AUDIO NATURAL\n"
        "==================================================\n\n"
        "Bloco O QUE FALAR = roteiro do audio. 10-30 segundos, 60-90\n"
        "palavras. Linguagem falada, sem jargao, soa como conversa real.\n\n"

        "==================================================\n"
        "CONTEXTO DO NEGOCIO (o que voce vende)\n"
        "==================================================\n\n"
        + prompt_vendedor + "\n\n"

        "==================================================\n"
        "CRM DO CLIENTE (interno, invisivel)\n"
        "==================================================\n\n"
        + crm_txt + "\n\n"

        "==================================================\n"
        "HISTORICO DA CONVERSA\n"
        "==================================================\n\n"
        + hist_txt + "\n\n"

        "==================================================\n"
        "MENSAGEM ATUAL DO CLIENTE\n"
        "==================================================\n\n"
        + mensagem_cliente + "\n\n"

        "==================================================\n"
        "FORMATO DE RESPOSTA OBRIGATORIO\n"
        "==================================================\n\n"
        "Responda EXATAMENTE com os 4 marcadores abaixo, cada um em uma\n"
        "linha sozinha. Nada fora dos blocos.\n\n"
        "=== O QUE FALAR ===\n"
        "(roteiro do audio, natural, 10-30s, terminando com UMA pergunta\n"
        "util OU proximo passo)\n\n"
        "=== TEXTO PARA ENVIAR ===\n"
        "REGRA CRITICA: O padrao e a palavra NENHUM.\n"
        "Voce SO preenche este bloco em 3 casos:\n"
        "1) Preco/pagamento (ex: 'R$ 120')\n"
        "2) Link/endereco (ex: 'Instagram: @x')\n"
        "3) Info tecnica copiavel (ex: 'PIX 123456')\n"
        "PROIBIDO copiar o roteiro do audio aqui.\n"
        "PROIBIDO colocar texto longo aqui.\n"
        "Se for conversa normal (pergunta, resposta), escreva: NENHUM\n\n"
        "=== ESTAGIO ===\n"
        "(APENAS UM: Novo Lead, Em Atendimento, Negociacao, Cliente, Perdido)\n\n"
        "=== LINHA CRM ===\n"
        "(Nome: xxx; Nicho: xxx; Objetivo: xxx; Dor: xxx; Objecao: xxx;\n"
        "Estrategia: xxx; Interesse: xxx; Status: xxx; Proximo passo: xxx)\n"
    )

    try:
        r = client.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "system", "content": "Voce e um closer consultivo. Entende antes de recomendar. Nunca vende no primeiro contato. Nunca repete saudacao se ja conversou. Uma pergunta por vez. Nunca fica em interrogatorio. Se receber INSTRUCAO DIRETA DO VENDEDOR, executa direto sem responder 'claro'. Nunca usa frases genericas. Responda SEMPRE com os 4 blocos exatos. TEXTO PARA ENVIAR e NENHUM em 90% dos casos (so preco/link/info tecnica). NUNCA copie o roteiro do audio pro bloco de texto."},
                {"role": "user", "content": prompt}
            ],
            timeout=60,
            temperature=0.7
        )
        return separar_resposta(r.choices[0].message.content)
    except Exception as e:
        return {"o_que_falar": "ERRO NA API: " + str(e), "texto_para_enviar": "NENHUM", "estagio": "Em Atendimento", "linha_crm": ""}


def gerar_prompt_vendedor(produto, publico, preco, dor, objecao, diferencial, tom):
    return (
        "# O QUE VENDE\n\n" + (produto or "") + "\n\n"
        "# PUBLICO-ALVO\n\n" + (publico or "") + "\n\n"
        "# PRECO\n\n" + (preco or "") + "\n\n"
        "# DOR PRINCIPAL DO CLIENTE\n\n" + (dor or "") + "\n\n"
        "# OBJECOES MAIS COMUNS\n\n" + (objecao or "") + "\n\n"
        "# DIFERENCIAL\n\n" + (diferencial or "") + "\n\n"
        "# TOM DE VOZ\n\n" + (tom or "") + "\n\n"
        "# REGRAS ESPECIFICAS\n\n"
        "- Use SOMENTE as informacoes acima para falar do produto\n"
        "- Nunca invente preco, prazo, beneficio ou condicao\n"
        "- Se nao souber algo, diga que vai confirmar\n"
        "- Adapte a linguagem ao tom definido\n"
    )


def avaliar_nicho_ia(produto, publico, preco, dor, objecao, diferencial, tom):
    import json
    try:
        client_local = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = (
            "Voce e especialista em marketing e vendas. Analise a qualidade\n"
            "dessas respostas de um vendedor configurando sua IA.\n\n"
            "PRODUTO: " + (produto or "") + "\n"
            "PUBLICO: " + (publico or "") + "\n"
            "PRECO: " + (preco or "") + "\n"
            "DOR: " + (dor or "") + "\n"
            "OBJECAO: " + (objecao or "") + "\n"
            "DIFERENCIAL: " + (diferencial or "") + "\n"
            "TOM: " + (tom or "") + "\n\n"
            "Analise a QUALIDADE pensando em: um vendedor humano usaria isso?\n"
            "Uma IA consegue trabalhar com essa info?\n\n"
            "DETECTE:\n"
            "- Campo vazio ou curto (<10 caracteres)\n"
            "- Generico: 'todo tipo de clientes', 'qualquer pessoa'\n"
            "- Confuso: '90 + 30 total 120'\n"
            "- Sem especificidade\n\n"
            "NOTA: 9-10 excelente, 7-8 bom, 5-6 mediocre, 3-4 ruim, 0-2 inutil\n\n"
            "Responda APENAS JSON sem markdown:\n"
            "{\"nota\": 7, \"problemas\": [\"problema 1\"], \"sugestoes\": {\"produto\": \"...\", \"publico\": \"...\", \"preco\": \"...\", \"dor\": \"...\", \"objecao\": \"...\", \"diferencial\": \"...\", \"tom\": \"...\"}}"
        )
        r = client_local.chat.completions.create(
            model=MODELO,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1500,
        )
        t = r.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
        d = json.loads(t)
        return {"nota": d.get("nota", 5), "problemas": d.get("problemas", []), "sugestoes": d.get("sugestoes", {})}
    except Exception as e:
        print("Erro avaliar_nicho_ia: " + str(e))
        return {"nota": 5, "problemas": ["Nao foi possivel avaliar"], "sugestoes": {}}


def enriquecer_prompt(produto, publico, preco, dor, objecao, diferencial, tom):
    import json
    try:
        client_local = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = (
            "Voce e especialista em vendas. O vendedor preencheu rapido e pode\n"
            "ter deixado campos vagos. Reescreva APENAS os campos vagos.\n\n"
            "PRODUTO: " + (produto or "") + "\n"
            "PUBLICO: " + (publico or "") + "\n"
            "PRECO: " + (preco or "") + "\n"
            "DOR: " + (dor or "") + "\n"
            "OBJECAO: " + (objecao or "") + "\n"
            "DIFERENCIAL: " + (diferencial or "") + "\n"
            "TOM: " + (tom or "") + "\n\n"
            "REGRAS:\n"
            "- Se campo ja esta bom, repita igual\n"
            "- NUNCA invente dados (ex: nao criar preco do nada)\n"
            "- PODE tornar generico em especifico\n\n"
            "Exemplos:\n"
            "- 'todo tipo de clientes' -> 'donos de lanchonete que querem vender mais a noite'\n"
            "- 'A combinar' -> 'Sob consulta, depende do escopo'\n\n"
            "Responda APENAS JSON sem markdown:\n"
            "{\"produto\": \"...\", \"publico\": \"...\", \"preco\": \"...\", \"dor\": \"...\", \"objecao\": \"...\", \"diferencial\": \"...\", \"tom\": \"...\"}"
        )
        r = client_local.chat.completions.create(
            model=MODELO,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000,
        )
        t = r.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
        d = json.loads(t)
        return {
            "produto": d.get("produto", produto),
            "publico": d.get("publico", publico),
            "preco": d.get("preco", preco),
            "dor": d.get("dor", dor),
            "objecao": d.get("objecao", objecao),
            "diferencial": d.get("diferencial", diferencial),
            "tom": d.get("tom", tom)
        }
    except Exception as e:
        print("Erro enriquecer_prompt: " + str(e))
        return {"produto": produto, "publico": publico, "preco": preco, "dor": dor, "objecao": objecao, "diferencial": diferencial, "tom": tom}


def validar_nicho_ia(nome, produto):
    import json
    try:
        client_local = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = (
            "Valida esse nicho.\n\n"
            "Nome: " + (nome or "") + "\n"
            "Vende: " + (produto or "")[:500] + "\n\n"
            "Responda APENAS JSON sem markdown:\n"
            "{\"valido\": true, \"motivo\": \"ok\"}\n"
            "ou\n"
            "{\"valido\": false, \"motivo\": \"explicacao\"}\n\n"
            "Bloqueie se: mistura 2 produtos, e vago, ou nao faz sentido."
        )
        r = client_local.chat.completions.create(
            model=MODELO,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=150,
        )
        t = r.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
        d = json.loads(t)
        return d.get("valido", True), d.get("motivo", "")
    except Exception as e:
        print("Erro validar_nicho_ia: " + str(e))
        return True, ""