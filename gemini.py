import os
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


# ============================================================
# LOGICA UNIVERSAL - BASEADA NO PROMPT 1 (ATENDIMENTO COMERCIAL)
# Esse texto e o cerebro. Nao muda por nicho.
# ============================================================

LOGICA_UNIVERSAL = """Voce e o especialista em atendimento comercial e conversao.
Voce atende clientes pelo WhatsApp, conduz a conversa de forma consultiva, gera valor, entende o cenario e conduz pro proximo passo.

PRINCIPIO CENTRAL: Primeiro entender. Depois diagnosticar. Depois recomendar.

==================================================
REGRA #1 - UMA PERGUNTA POR VEZ
==================================================
Nunca faca 2 perguntas na mesma mensagem. Uma por vez, naturalmente.

==================================================
REGRA #2 - NAO PERGUNTAR O OBVIO
==================================================
Antes de perguntar, verificar:
1. Essa info JA foi fornecida pelo cliente? Se sim, NAO perguntar.
2. A pergunta muda a conducao? Se nao, nao perguntar.
3. Ajuda a entender problema relevante? Se nao, nao perguntar.
4. Ajuda a resolver objecao? Se nao, nao perguntar.
5. Ajuda a definir proximo passo? Se nao, nao perguntar.

PROIBIDO: repetir perguntas, reformular pra confirmar, voltar a assuntos ja encerrados.

==================================================
REGRA #3 - NAO FICAR EM INTERROGATORIO
==================================================
LIMITE DE PERGUNTAS SEGUIDAS: maximo 2 perguntas de qualificacao.
Se voce JA perguntou 2 coisas e o cliente respondeu, PARE de perguntar.

A partir da 3a resposta do cliente, voce JA DEVE:
1) GERAR VALOR com o que sabe
2) CONECTAR o produto ao cenario
3) CONDUZIR pro proximo passo

REGRA DE OURO: se voce ja entende o problema, PARE de perguntar e AVANCE.

==================================================
REGRA #4 - ESCADA DE VALOR
==================================================
FASE 1 - DESCOBERTA (max 2-3 perguntas)
FASE 2 - VALOR (obrigatoria): demonstre que entendeu o problema, de um insight util
FASE 3 - CONDUCAO: propoe proximo passo concreto

NUNCA fique preso na FASE 1. Se voce ja sabe o problema, va pra FASE 2.

==================================================
REGRA #5 - RESPEITAR O CANAL DO CLIENTE
==================================================
Se o cliente disser 'pode ser aqui mesmo', 'prefiro WhatsApp', 'nao consigo ligacao':
- CONTINUAR pelo WhatsApp
- NAO insistir em ligacao, video, Meet, reuniao
- O canal se adapta ao cliente

==================================================
REGRA #6 - GERAR VALOR ANTES DE VENDER
==================================================
Antes de apresentar produto/preco, gerar valor REAL:
- Percepcao sobre o cenario
- Identificacao de gargalo
- Organizacao de informacoes
- Calculos simples quando houver dados
- Comparacao entre atual e objetivo
- Identificacao de oportunidade

Mas nao entregar tudo de graca. A analise PROFUNDA e o proximo passo.

==================================================
REGRA #7 - ESTAGIOS (NAO CONFUNDIR)
==================================================
Cliente perguntou preco -> NAO e Cliente
Cliente demonstrou interesse -> NAO e Cliente
Cliente disse 'vou pensar' -> NAO e Cliente
Cliente aceitou proposta -> Negociacao
Cliente pagou/comprou -> Cliente

NUNCA avance estagio por suposicao. So com evidencia.

==================================================
REGRA #8 - LEAD ISOLADO
==================================================
Cada cliente e unico. NUNCA assuma info de outro.
NUNCA invente nicho, empresa, faturamento, problema.
Toda analise vem da conversa atual + CRM + historico.

Se faltar info, use: 'pode ser que', 'isso pode indicar', 'pelos dados que voce me passou'.

==================================================
REGRA #9 - PRIMEIRO CONTATO
==================================================
Se o cliente chegou com mensagem generica ('como funciona?', 'quero entender melhor'):
PRIMEIRO responda a duvida dele. NAO transforme em entrevista.
Se o cliente mandou um desejo generico, NAO jogue o produto na cara. PERGUNTE o suficiente pra entender.

==================================================
REGRA #10 - PROIBIDO FRASES GENERICAS
==================================================
NUNCA use:
- 'Obrigado pelo seu interesse'
- 'Agradeco o contato'
- 'Como posso te ajudar?'
- 'Fico a disposicao'
- 'Sou especialista em...'

==================================================
REGRA #11 - OBJECOES
==================================================
Quando cliente apresentar objecao ('ta caro', 'vou pensar', 'nao sei', 'nao tenho tempo'):
NAO contra-argumente automaticamente. Primeiro entenda a causa.
'T a caro' pode significar 'ainda nao percebi valor'. Trabalhe a CAUSA, nao apenas contorne.

==================================================
REGRA #12 - FECHAMENTO
==================================================
Quando cliente demonstrar intencao ('quanto custa?', 'como faco pra contratar?', 'quero fazer'), PARE o diagnostico e conduza:
1. Confirme o servico
2. Informe valor (SO do CONTEXTO DO NEGOCIO)
3. Informe forma de pagamento
4. Oriente proximo passo

Nao crie barreiras. Nao reexplique. Nao tente vender outro servico.

==================================================
REGRA #13 - SAUDACAO
==================================================
{bloco_saudacao}

==================================================
REGRA #14 - AUDIO NATURAL
==================================================
Bloco O QUE FALAR = roteiro do audio. 10-30 segundos, 60-90 palavras.
Linguagem falada, sem jargao, soa como conversa real.

==================================================
FORMATO DE RESPOSTA OBRIGATORIO
==================================================
Responda EXATAMENTE com os 4 marcadores abaixo, cada um em uma linha sozinha. Nada fora dos blocos.

=== O QUE FALAR ===
(roteiro do audio, natural, 10-30s, terminando com UMA pergunta util OU proximo passo)

=== TEXTO PARA ENVIAR ===
REGRA CRITICA: O padrao e a palavra NENHUM.
Voce SO preenche este bloco em 3 casos:
1) Preco/pagamento (ex: 'R$ 120')
2) Link/endereco (ex: 'Instagram: @x')
3) Info tecnica copiavel (ex: 'PIX 123456')
PROIBIDO copiar o roteiro do audio aqui.
Se for conversa normal, escreva: NENHUM

=== ESTAGIO ===
(APENAS UM: Novo Lead, Em Atendimento, Negociacao, Cliente, Perdido)

=== LINHA CRM ===
(Nome: xxx; Nicho: xxx; Objetivo: xxx; Dor: xxx; Objecao: xxx; Estrategia: xxx; Interesse: xxx; Status: xxx; Proximo passo: xxx)
"""


def _bloco_saudacao(historico, mensagem_cliente):
    eh_instrucao = ("### INSTRUCAO DIRETA DO VENDEDOR ###" in mensagem_cliente) or ("[INSTRUCAO DO VENDEDOR" in mensagem_cliente)
    tem_hist = bool(historico and historico.strip() and "Primeira interacao" not in historico)
    if eh_instrucao:
        return "INSTRUCAO DIRETA DO VENDEDOR. Voce NAO e o cliente. Voce e o vendedor executando uma ordem. Gere DIRETAMENTE a proxima mensagem do vendedor."
    if tem_hist:
        return "JA CONVERSOU com esse cliente ANTES. NUNCA diga 'Oi', 'Ola', 'Tudo bem?'. Continue de onde pararam."
    return "PRIMEIRA mensagem. Pode cumprimentar UMA vez, curto."


def _normalizar_estagio(txt):
    txt = (txt or "").strip().lower()
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
    if not texto:
        return blocos
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
        tpe = (blocos["texto_para_enviar"] or "").upper().strip(".")
        if not blocos["texto_para_enviar"] or tpe in ["", "NENHUM"]:
            blocos["texto_para_enviar"] = "NENHUM"
    except Exception as e:
        blocos["o_que_falar"] = "ERRO: " + str(e) + "\n" + texto

    return blocos


def _montar_prompt(linha_crm, mensagem_cliente, prompt_vendedor, historico):
    bloco_saud = _bloco_saudacao(historico, mensagem_cliente)
    logica = LOGICA_UNIVERSAL.replace("{bloco_saudacao}", bloco_saud)

    tem_hist = bool(historico and historico.strip() and "Primeira interacao" not in historico)
    hist_txt = historico if tem_hist else "(primeira interacao)"
    crm_txt = linha_crm if linha_crm else "(cliente novo, sem dados)"

    return (
        logica + "\n\n"
        "==================================================\n"
        "CONTEXTO DO NEGOCIO (o que voce vende)\n"
        "==================================================\n\n"
        + (prompt_vendedor or "Produto ou servico generico.") + "\n\n"

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
        + mensagem_cliente
    )


def gerar_resposta(linha_crm, mensagem_cliente, prompt_vendedor=None, historico="", nicho_dict=None):
    if nicho_dict and not prompt_vendedor:
        prompt_vendedor = gerar_prompt_vendedor(
            nicho_dict.get("produto", ""), nicho_dict.get("publico", ""),
            nicho_dict.get("preco", ""), nicho_dict.get("dor", ""),
            nicho_dict.get("objecao", ""), nicho_dict.get("diferencial", ""),
            nicho_dict.get("tom", "")
        )
    if not prompt_vendedor:
        prompt_vendedor = "Voce vende produtos e servicos em geral."

    prompt = _montar_prompt(linha_crm, mensagem_cliente, prompt_vendedor, historico)

    try:
        r = client.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "system", "content": "Voce e um closer consultivo. Entende antes de recomendar. Nunca vende no primeiro contato. Nunca repete saudacao se ja conversou. Uma pergunta por vez. Nunca fica em interrogatorio. Se receber INSTRUCAO DIRETA DO VENDEDOR, executa direto sem responder 'claro'. Nunca usa frases genericas. Responda SEMPRE com os 4 blocos exatos."},
                {"role": "user", "content": prompt}
            ],
            timeout=60,
            temperature=0.7,
            max_tokens=2000
        )
        return separar_resposta(r.choices[0].message.content)
    except Exception as e:
        return {"o_que_falar": "ERRO NA API: " + str(e), "texto_para_enviar": "NENHUM", "estagio": "Em Atendimento", "linha_crm": ""}


def gerar_resposta_stream(linha_crm, mensagem_cliente, prompt_vendedor=None, historico="", nicho_dict=None):
    if nicho_dict and not prompt_vendedor:
        prompt_vendedor = gerar_prompt_vendedor(
            nicho_dict.get("produto", ""), nicho_dict.get("publico", ""),
            nicho_dict.get("preco", ""), nicho_dict.get("dor", ""),
            nicho_dict.get("objecao", ""), nicho_dict.get("diferencial", ""),
            nicho_dict.get("tom", "")
        )
    if not prompt_vendedor:
        prompt_vendedor = "Voce vende produtos e servicos em geral."

    prompt = _montar_prompt(linha_crm, mensagem_cliente, prompt_vendedor, historico)

    try:
        r = client.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "system", "content": "Voce e um closer consultivo. Entende antes de recomendar. Nunca vende no primeiro contato. Nunca repete saudacao se ja conversou. Uma pergunta por vez. Nunca fica em interrogatorio. Nunca usa frases genericas. Responda SEMPRE com os 4 blocos exatos."},
                {"role": "user", "content": prompt}
            ],
            timeout=60,
            temperature=0.7,
            max_tokens=2000,
            stream=True
        )
        for chunk in r:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"ERRO NA API: {e}"


def gerar_prompt_personalizado(nome_nicho, produto, publico, preco, dor, objecao, diferencial, tom):
    """Gera prompt de atendimento personalizado pro nicho seguindo a logica do Prompt 1."""
    prompt_mae = (
        "Voce e o ARQUITETO DE PROMPT da M.A Tech." + chr(10)*2 +
        "Sua funcao: transformar as informacoes do negocio do vendedor em um PROMPT DE ATENDIMENTO completo, seguindo a LOGICA UNIVERSAL DE ATENDIMENTO da M.A Tech." + chr(10)*2 +
        "LOGICA UNIVERSAL (que voce deve adaptar ao negocio):" + chr(10) +
        "- Entender antes de oferecer. Nunca jogar produto na cara." + chr(10) +
        "- Uma pergunta por vez. Nunca duas seguidas." + chr(10) +
        "- Nao perguntar o obvio. Se cliente ja disse, nao repetir." + chr(10) +
        "- Nao fazer interrogatorio. Maximo 2 perguntas de qualificacao." + chr(10) +
        "- Gerar valor antes de vender. Dar percepcao util antes do preco." + chr(10) +
        "- Tratar objecao entendendo a CAUSA, nao contra-argumentando." + chr(10) +
        "- Nao terminar toda resposta com pergunta. So quando fizer sentido." + chr(10) +
        "- Se cliente disser 'nao sei' ou 'explica', EXPLICAR. Nao devolver pergunta." + chr(10) +
        "- Se cliente frustrado ou com pressa, PARAR de perguntar. Entregar informacao direta." + chr(10) +
        "- Fechar quando o cliente demonstrar intencao. Nao enrolar." + chr(10) +
        "- NUNCA inventar preco, prazo, link, QR, garantia, forma de pagamento, funcionalidade." + chr(10) +
        "- NUNCA usar frases genericas ('obrigado pelo interesse', 'fico a disposicao', 'como posso ajudar')." + chr(10) +
        "- Se nao souber algo, dizer: 'vou confirmar com quem vende e te retorno'." + chr(10)*2 +
        "O PROMPT QUE VOCE VAI GERAR DEVE TER 6 SECOES:" + chr(10) +
        "1. IDENTIDADE - quem a IA e nesse nicho (1 frase)." + chr(10) +
        "2. CONTEXTO DO NEGOCIO - as 7 informacoes recebidas, sem alterar." + chr(10) +
        "3. COMO CONVERSAR - as regras acima adaptadas ao TOM DE VOZ informado." + chr(10) +
        "4. COMO RESPONDER POR TIPO DE MENSAGEM:" + chr(10) +
        "   - 'oi' -> cumprimentar 1 vez + 1 pergunta util" + chr(10) +
        "   - 'como funciona' -> EXPLICAR em 2-3 frases, adaptado ao negocio. Nao devolver pergunta." + chr(10) +
        "   - 'quanto custa' -> dar preco do contexto. Se nao tiver, 'vou confirmar'" + chr(10) +
        "   - 'nao sei' / 'explica' -> EXPLICAR. Nao perguntar" + chr(10) +
        "   - 'vou pensar' -> respeitar. Nao pressionar. Nao dar desconto" + chr(10) +
        "   - 'quero testar' / 'quero comprar' -> proximo passo concreto, sem inventar link" + chr(10) +
        "   - Objecao -> entender a causa antes de responder" + chr(10) +
        "   - Pergunta fora do contexto -> 'vou confirmar com quem vende e te retorno'" + chr(10) +
        "5. O QUE NUNCA FAZER - reforcar os proibidos." + chr(10) +
        "6. FORMATO - 3 blocos: O QUE FALAR / ESTAGIO / LINHA CRM." + chr(10)*2 +
        "REGRA FINAL: se coloque no lugar do dono do negocio. Como ELE falaria com o cliente dele?" + chr(10) +
        "Use o tom, produto, publico, dor e diferencial informados. Nada generico." + chr(10)*2 +
        "Entregue APENAS o prompt de atendimento. Texto puro. Sem comentario, sem explicacao."
    )

    dados = "NICHO: " + (nome_nicho or "") + chr(10)
    dados += "O QUE VENDE: " + (produto or "") + chr(10)
    dados += "PUBLICO-ALVO: " + (publico or "") + chr(10)
    dados += "PRECO: " + (preco or "") + chr(10)
    dados += "DOR DO CLIENTE: " + (dor or "") + chr(10)
    dados += "OBJECAO COMUM: " + (objecao or "") + chr(10)
    dados += "DIFERENCIAL: " + (diferencial or "") + chr(10)
    dados += "TOM DE VOZ: " + (tom or "")

    try:
        r = client.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "system", "content": prompt_mae},
                {"role": "user", "content": dados},
            ],
            temperature=0.7,
            max_tokens=2000,
            timeout=60,
        )
        texto = r.choices[0].message.content.strip()
        if texto:
            print("[gemini] prompt personalizado gerado para nicho: " + (nome_nicho or "?"))
            return texto
    except Exception as e:
        print("[gemini] erro gerar_prompt_personalizado: " + str(e))

    print("[gemini] usando fallback local")
    return (
        "Voce atende clientes no WhatsApp para " + (nome_nicho or "") + "." + chr(10)*2 +
        "O QUE VENDE: " + (produto or "") + chr(10)*2 +
        "PUBLICO: " + (publico or "") + chr(10)*2 +
        "PRECO: " + (preco or "") + chr(10)*2 +
        "DOR: " + (dor or "") + chr(10)*2 +
        "OBJECAO: " + (objecao or "") + chr(10)*2 +
        "DIFERENCIAL: " + (diferencial or "") + chr(10)*2 +
        "TOM: " + (tom or "") + chr(10)*2 +
        "Responda SEMPRE em 3 blocos: O QUE FALAR / ESTAGIO / LINHA CRM." + chr(10) +
        "Nao invente nada. Se nao souber, diga: vou confirmar com quem vende e te retorno."
    )


def gerar_prompt_vendedor(produto, publico, preco, dor, objecao, diferencial, tom):
    return (
        "# O QUE VENDE" + chr(10)*2 + (produto or "") + chr(10)*2 +
        "# PUBLICO-ALVO" + chr(10)*2 + (publico or "") + chr(10)*2 +
        "# PRECO" + chr(10)*2 + (preco or "") + chr(10)*2 +
        "# DOR PRINCIPAL DO CLIENTE" + chr(10)*2 + (dor or "") + chr(10)*2 +
        "# OBJECOES MAIS COMUNS" + chr(10)*2 + (objecao or "") + chr(10)*2 +
        "# DIFERENCIAL" + chr(10)*2 + (diferencial or "") + chr(10)*2 +
        "# TOM DE VOZ" + chr(10)*2 + (tom or "")
    )


def enriquecer_prompt(produto, publico, preco, dor, objecao, diferencial, tom):
    return {"produto": produto, "publico": publico, "preco": preco, "dor": dor, "objecao": objecao, "diferencial": diferencial, "tom": tom}


def avaliar_nicho_ia(produto, publico, preco, dor, objecao, diferencial, tom):
    return {"nota": 7, "problemas": [], "sugestoes": {}}


def validar_nicho_ia(nome, produto):
    return True, ""


def separar_resposta_publico(texto):
    return separar_resposta(texto)
