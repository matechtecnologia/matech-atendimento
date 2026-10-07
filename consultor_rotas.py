# consultor_rotas.py
# M.A Tech — Rotas da Consultoria Empresarial
# API JSON + tela inicial + painel de status + historico + passos.
# Chamado por consultor_install.py no boot do app.


from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse


# ============================================================
# LIMITES DIARIOS POR PLANO
# ============================================================
LIMITES_DIARIOS = {
    "gratis": 5,
    "basico": 20,
    "pro": 60,
    "empresarial": 200,
}

# Nomes amigaveis dos servicos (pra exibir no painel e no historico)
NOMES_SERVICOS = {
    "atendimento_ia": "M.A Tech Atendimento com IA",
    "gestao": "M.A Tech Gestao",
    "trafego": "M.A Tech Trafego Pago",
    "crm": "M.A Tech CRM",
    "automacao": "M.A Tech Automacao",
}


# ============================================================
# LIMPEZA DE UNICODE
# ============================================================
def _limpar_unicode(texto):
    if not texto:
        return texto
    problematicos = {
        "\u202f": " ",
        "\u00a0": " ",
        "\u2009": " ",
        "\u200a": " ",
        "\u200b": "",
        "\u200c": "",
        "\u200d": "",
        "\ufeff": "",
    }
    for antigo, novo in problematicos.items():
        texto = texto.replace(antigo, novo)
    return texto


# ============================================================
# HELPERS INTERNOS
# ============================================================
def _get_vendedor_id(usuario_id, get_conn, close_conn):
    if not usuario_id:
        return None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id FROM vendedores WHERE usuario_id = %s", (int(usuario_id),))
        v = cur.fetchone()
        cur.close()
        close_conn(conn)
        return v[0] if v else None
    except Exception as e:
        print(f"Consultor: erro ao buscar vendedor_id - {e}")
        try:
            close_conn(conn)
        except Exception:
            pass
        return None


def _get_plano(vendedor_id, get_conn, close_conn):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT plano FROM vendedores WHERE id = %s", (vendedor_id,))
        r = cur.fetchone()
        cur.close()
        close_conn(conn)
        return (r[0] or "gratis").lower() if r else "gratis"
    except Exception:
        try:
            close_conn(conn)
        except Exception:
            pass
        return "gratis"


def _uso_hoje(vendedor_id, get_conn, close_conn):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT COALESCE(total, 0) FROM consultoria_uso
            WHERE vendedor_id = %s AND data = CURRENT_DATE
        """, (vendedor_id,))
        r = cur.fetchone()
        cur.close()
        close_conn(conn)
        return int(r[0]) if r else 0
    except Exception:
        try:
            close_conn(conn)
        except Exception:
            pass
        return 0


def _incrementar_uso(vendedor_id, get_conn, close_conn):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO consultoria_uso (vendedor_id, data, total)
            VALUES (%s, CURRENT_DATE, 1)
            ON CONFLICT (vendedor_id, data)
            DO UPDATE SET total = consultoria_uso.total + 1
        """, (vendedor_id,))
        conn.commit()
        cur.close()
        close_conn(conn)
        return True
    except Exception as e:
        print(f"Consultor: erro ao incrementar uso - {e}")
        try:
            close_conn(conn)
        except Exception:
            pass
        return False


def _get_consultoria_ativa(vendedor_id, get_conn, close_conn):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id FROM consultorias
            WHERE vendedor_id = %s AND status = 'ativa'
            ORDER BY id DESC LIMIT 1
        """, (vendedor_id,))
        r = cur.fetchone()
        cur.close()
        close_conn(conn)
        return r[0] if r else None
    except Exception:
        try:
            close_conn(conn)
        except Exception:
            pass
        return None


def _get_mensagens(consultoria_id, get_conn, close_conn):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT direcao, mensagem, criado_em
            FROM consultoria_mensagens
            WHERE consultoria_id = %s
            ORDER BY id ASC
        """, (consultoria_id,))
        linhas = cur.fetchall()
        cur.close()
        close_conn(conn)
        return [{"direcao": r[0], "mensagem": r[1], "criado_em": r[2].isoformat() if r[2] else None} for r in linhas]
    except Exception as e:
        print(f"Consultor: erro ao buscar mensagens - {e}")
        try:
            close_conn(conn)
        except Exception:
            pass
        return []


def _salvar_mensagem(consultoria_id, direcao, mensagem, get_conn, close_conn):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO consultoria_mensagens (consultoria_id, direcao, mensagem)
            VALUES (%s, %s, %s)
        """, (consultoria_id, direcao, mensagem))
        conn.commit()
        cur.close()
        close_conn(conn)
        return True
    except Exception as e:
        print(f"Consultor: erro ao salvar mensagem - {e}")
        try:
            close_conn(conn)
        except Exception:
            pass
        return False


def _consultoria_e_nova(consultoria_id, get_conn, close_conn):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT EXTRACT(EPOCH FROM (NOW() - criado_em)) < 60
            FROM consultorias WHERE id = %s
        """, (consultoria_id,))
        r = cur.fetchone()
        cur.close()
        close_conn(conn)
        return bool(r and r[0])
    except Exception:
        try:
            close_conn(conn)
        except Exception:
            pass
        return False


def _get_passos(consultoria_id, get_conn, close_conn):
    """Devolve a lista de passos do plano de acao."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, ordem, titulo, acao, prazo, concluido, concluido_em
            FROM consultoria_passos
            WHERE consultoria_id = %s
            ORDER BY ordem ASC, id ASC
        """, (consultoria_id,))
        linhas = cur.fetchall()
        cur.close()
        close_conn(conn)
        return [
            {
                "id": r[0],
                "ordem": r[1],
                "titulo": r[2] or "",
                "acao": r[3] or "",
                "prazo": r[4] or "essa semana",
                "concluido": bool(r[5]),
                "concluido_em": r[6].isoformat() if r[6] else None,
            }
            for r in linhas
        ]
    except Exception as e:
        print(f"Consultor: erro ao buscar passos - {e}")
        try:
            close_conn(conn)
        except Exception:
            pass
        return []


def _salvar_passos(consultoria_id, passos, get_conn, close_conn):
    """Substitui todos os passos da consultoria pelos novos.
    Apaga os antigos e insere os novos. Mantem concluidos se titulo for igual."""
    if not passos:
        return False
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT titulo, concluido, concluido_em
            FROM consultoria_passos
            WHERE consultoria_id = %s AND concluido = TRUE
        """, (consultoria_id,))
        concluidos_antigos = {r[0]: (r[1], r[2]) for r in cur.fetchall()}

        cur.execute("DELETE FROM consultoria_passos WHERE consultoria_id = %s", (consultoria_id,))

        for i, p in enumerate(passos):
            titulo = _limpar_unicode(str(p.get("titulo") or "").strip())[:120]
            acao = _limpar_unicode(str(p.get("acao") or "").strip())[:300]
            prazo = _limpar_unicode(str(p.get("prazo") or "essa semana").strip())[:30]
            if not titulo or not acao:
                continue
            ordem = i + 1
            ja_concluido = titulo in concluidos_antigos
            concluido_em = concluidos_antigos[titulo][1] if ja_concluido else None
            cur.execute("""
                INSERT INTO consultoria_passos
                    (consultoria_id, ordem, titulo, acao, prazo, concluido, concluido_em)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (consultoria_id, ordem, titulo, acao, prazo, ja_concluido, concluido_em))

        conn.commit()
        cur.close()
        close_conn(conn)
        return True
    except Exception as e:
        print(f"Consultor: erro ao salvar passos - {e}")
        try:
            close_conn(conn)
        except Exception:
            pass
        return False


def _get_status_completo(vendedor_id, consultoria_id, get_conn, close_conn):
    """Devolve um dict com todo o status da consultoria atual."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, status, gargalo_detectado, servico_indicado,
                   criado_em, atualizado_em
            FROM consultorias WHERE id = %s
        """, (consultoria_id,))
        r = cur.fetchone()
        if not r:
            cur.close()
            close_conn(conn)
            return None

        cur.execute("""
            SELECT COUNT(*) FROM consultoria_mensagens
            WHERE consultoria_id = %s
        """, (consultoria_id,))
        total_msgs = cur.fetchone()[0] or 0

        cur.close()
        close_conn(conn)

        plano = _get_plano(vendedor_id, get_conn, close_conn)
        limite = LIMITES_DIARIOS.get(plano, 5)
        usado = _uso_hoje(vendedor_id, get_conn, close_conn)

        servico_raw = (r[3] or "").strip().lower()
        servico_nome = NOMES_SERVICOS.get(servico_raw, servico_raw or "")

        passos = _get_passos(consultoria_id, get_conn, close_conn)
        total_passos = len(passos)
        concluidos = sum(1 for p in passos if p["concluido"])

        return {
            "id": r[0],
            "status": r[1] or "ativa",
            "gargalo_detectado": r[2] or "",
            "servico_indicado": servico_raw,
            "servico_nome": servico_nome,
            "criado_em": r[4].isoformat() if r[4] else None,
            "atualizado_em": r[5].isoformat() if r[5] else None,
            "total_mensagens": int(total_msgs),
            "plano": plano,
            "limite": limite,
            "usado": usado,
            "restantes": max(0, limite - usado),
            "passos": passos,
            "passos_total": total_passos,
            "passos_concluidos": concluidos,
        }
    except Exception as e:
        print(f"Consultor: erro ao montar status - {e}")
        try:
            close_conn(conn)
        except Exception:
            pass
        return None


def _get_historico(vendedor_id, get_conn, close_conn, excluir_id=None):
    """Lista consultorias encerradas que tem pelo menos 1 mensagem."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        sql = """
            SELECT c.id, c.gargalo_detectado, c.servico_indicado,
                   c.criado_em, c.atualizado_em,
                   (SELECT COUNT(*) FROM consultoria_mensagens m
                    WHERE m.consultoria_id = c.id) AS total_msgs
            FROM consultorias c
            WHERE c.vendedor_id = %s AND c.status = 'encerrada'
        """
        params = [vendedor_id]
        if excluir_id:
            sql += " AND c.id <> %s"
            params.append(excluir_id)
        sql += " ORDER BY c.id DESC LIMIT 30"

        cur.execute(sql, tuple(params))
        linhas = cur.fetchall()
        cur.close()
        close_conn(conn)

        itens = []
        for r in linhas:
            if (r[5] or 0) == 0:
                continue
            servico_raw = (r[2] or "").strip().lower()
            itens.append({
                "id": r[0],
                "gargalo": (r[1] or "").strip(),
                "servico": servico_raw,
                "servico_nome": NOMES_SERVICOS.get(servico_raw, servico_raw or ""),
                "criado_em": r[3].isoformat() if r[3] else None,
                "atualizado_em": r[4].isoformat() if r[4] else None,
                "total_mensagens": int(r[5] or 0),
            })
        return itens
    except Exception as e:
        print(f"Consultor: erro ao buscar historico - {e}")
        try:
            close_conn(conn)
        except Exception:
            pass
        return []


def _gerar_msg_inicial(vendedor_id, consultoria_id, get_conn, close_conn):
    try:
        from consultor_core import montar_dossie, formatar_dossie_para_prompt
        from consultor import gerar_resposta_consultor

        dossie = montar_dossie(vendedor_id, get_conn, close_conn)
        dossie_txt = formatar_dossie_para_prompt(dossie)

        msg = gerar_resposta_consultor(
            mensagem_usuario="(inicio da consultoria - gere sua primeira mensagem para o vendedor, cumprimentando e conduzindo a conversa)",
            dossie_texto=dossie_txt,
            historico_texto="",
        )
        msg = _limpar_unicode(msg)
        _salvar_mensagem(consultoria_id, "consultor", msg, get_conn, close_conn)
    except Exception as e:
        print(f"Consultor: erro ao gerar msg inicial - {e}")


# ============================================================
# ETAPA 3 + 4A — ANALISE AUTOMATICA (2a chamada de IA)
# Extrai: gargalo + servico + plano de acao (passos)
# ============================================================
def _analisar_e_salvar(vendedor_id, consultoria_id, historico_txt, get_conn, close_conn):
    try:
        from groq import Groq
        import os as _os
        import json as _json
        import re as _re

        api_key = _os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Consultor: GROQ_API_KEY ausente na analise.")
            return

        try:
            _c = get_conn()
            _cu = _c.cursor()
            _cu.execute("SELECT gargalo_detectado, servico_indicado FROM consultorias WHERE id = %s", (consultoria_id,))
            _r = _cu.fetchone()
            _cu.execute("SELECT COUNT(*) FROM consultoria_passos WHERE consultoria_id = %s", (consultoria_id,))
            _n_passos = _cu.fetchone()[0] or 0
            _cu.close()
            close_conn(_c)
            if _r and _r[0] and _r[1] and _n_passos > 0:
                print(f"Consultor: analise pulada (consultoria #{consultoria_id} ja tem gargalo+servico+passos).")
                return
        except Exception:
            try:
                close_conn(_c)
            except Exception:
                pass

        prompt = f"""Analise a conversa abaixo entre um CONSULTOR da M.A Tech e um VENDEDOR.

============================================================
COMO O M.A TECH FUNCIONA (leia ANTES de gerar os passos)
============================================================

DIVISAO DE RESPONSABILIDADE:

O VENDEDOR (manual):
- Recebe a mensagem no canal dele (WhatsApp, Instagram, email)
- COPIA a mensagem e COLA dentro do M.A Tech
- COPIA o texto pronto que a IA devolve e ENVIA no canal dele
- Confere a aba "Follow-ups" pra ver quem precisa de atencao

A IA (automatico - o cliente NAO faz nada):
- Le o historico do cliente e o nicho
- Devolve: O QUE FALAR + TEXTO PRONTO + ESTAGIO + LINHA CRM
- REGISTRA o lead automaticamente no funil
- AGENDA o follow-up sozinha, com a data sugerida
- MOSTRA na aba Follow-ups quem esta atrasado

============================================================
O QUE NAO EXISTE (nunca sugira)
============================================================

NAO existe:
- Conectar WhatsApp / Instagram / email na plataforma
- Ler conversas automaticamente
- Responder cliente sozinho (bot/chatbot)
- Enviar mensagem automatica
- API do WhatsApp Business
- Disparo em massa
- Ajustar data e hora do follow-up (a IA agenda sozinha)
- Cadastrar lead manualmente (a IA faz automatico)
- Configurar integracao, API, webhook, token

============================================================
REGRA DOS PASSOS
============================================================

Cada passo = UMA acao MANUAL do vendedor dentro do M.A Tech.

NUNCA crie passo sobre o que a IA faz sozinha (registrar lead,
agendar follow-up, ler historico). Isso NAO e tarefa do vendedor.

NUNCA crie passo sobre configurar integracao, API, canal, etc.

BONS EXEMPLOS de passo:
- Colar a primeira mensagem no M.A Tech
- Testar a IA com um lead real
- Cadastrar um nicho (produto + cliente ideal)
- Abrir a aba Follow-ups todo dia pela manha
- Revisar o estagio dos leads abertos

MAUS EXEMPLOS de passo (NUNCA gere assim):
- Ajustar data e hora do follow-up (IA faz automatico)
- Cadastrar lead manualmente (IA faz automatico)
- Configurar integracao com WhatsApp (nao existe)
- Ativar envio automatico de mensagem (nao existe)

============================================================
SUA TAREFA
============================================================

Extrair 3 informacoes em formato JSON.
Se ainda nao houver informacao suficiente, retorne null nos campos e lista vazia nos passos.

- "gargalo": o problema principal do negocio do vendedor (frase curta, ate 60 chars)
- "servico": qual servico M.A Tech o consultor indicou ou esta indicando
  (valores aceitos: atendimento_ia, gestao, trafego, crm, automacao, nenhum)
- "passos": lista de 3 a 5 acoes MANUAIS do vendedor dentro do M.A Tech
  Cada passo tem:
    - "titulo": frase curta (ate 40 chars) - o que fazer
    - "acao": explicacao pratica em 1-2 frases (ate 200 chars)
    - "prazo": hoje, essa semana ou esse mes

Responda APENAS com JSON valido, sem texto extra, sem crase, sem markdown.

Formato exato:
{{"gargalo": "...", "servico": "...", "passos": [{{"titulo": "...", "acao": "...", "prazo": "..."}}]}}

CONVERSA:
{historico_txt}

JSON:"""

        cliente = Groq(api_key=api_key)
        try:
            resp = cliente.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.2,
            )
        except Exception:
            resp = cliente.chat.completions.create(
                model="qwen/qwen3.8-27b",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.2,
            )

        conteudo = (resp.choices[0].message.content or "").strip()
        print(f"Consultor: resposta bruta da 2a chamada = {conteudo[:300]!r}")

        m = _re.search(r'\{.*\}', conteudo, _re.DOTALL)
        if not m:
            print("Consultor: nenhum JSON encontrado na resposta.")
            return

        try:
            dados = _json.loads(m.group(0))
        except Exception as e:
            print(f"Consultor: JSON invalido - {e}")
            return

        gargalo = (dados.get("gargalo") or "").strip()
        servico = (dados.get("servico") or "").strip().lower()
        passos = dados.get("passos") or []

        validos = {"atendimento_ia", "gestao", "trafego", "crm", "automacao"}
        if servico not in validos:
            servico = None

        if gargalo:
            gargalo = _limpar_unicode(gargalo)[:200]
        if not gargalo and not servico and not passos:
            print("Consultor: nada util pra salvar.")
            return

        conn = get_conn()
        cur = conn.cursor()
        campos = []
        valores = []
        if gargalo:
            campos.append("gargalo_detectado = %s")
            valores.append(gargalo)
        if servico:
            campos.append("servico_indicado = %s")
            valores.append(servico)
        campos.append("atualizado_em = NOW()")
        valores.append(consultoria_id)

        sql = f"UPDATE consultorias SET {', '.join(campos)} WHERE id = %s"
        cur.execute(sql, tuple(valores))
        conn.commit()
        cur.close()
        close_conn(conn)

        if passos and isinstance(passos, list):
            _salvar_passos(consultoria_id, passos, get_conn, close_conn)
            print(f"Consultor: {len(passos)} passos salvos (consultoria #{consultoria_id})")

        print(f"Consultor: gargalo='{gargalo}' servico='{servico}' (consultoria #{consultoria_id})")

    except Exception as e:
        print(f"Consultor: erro na analise automatica - {e}")
        try:
            close_conn(conn)
        except Exception:
            pass


# ============================================================
# REGISTRO DAS ROTAS
# ============================================================
def registrar_rotas_consultor(app, get_conn, close_conn, Cookie, Request):

    from consultor_core import montar_dossie, formatar_dossie_para_prompt
    from consultor import gerar_resposta_consultor, formatar_historico

    @app.get("/consultoria", response_class=HTMLResponse)
    def tela_consultoria(request: Request,
                         usuario_id: str = Cookie(None),
                         usuario_nome: str = Cookie(None)):
        if not usuario_id:
            return RedirectResponse(url="/login")

        vendedor_id = _get_vendedor_id(usuario_id, get_conn, close_conn)
        if not vendedor_id:
            return RedirectResponse(url="/hub")

        plano = _get_plano(vendedor_id, get_conn, close_conn)
        limite = LIMITES_DIARIOS.get(plano, 5)
        usado = _uso_hoje(vendedor_id, get_conn, close_conn)
        consultoria_id = _get_consultoria_ativa(vendedor_id, get_conn, close_conn)

        if not consultoria_id:
            try:
                conn = get_conn()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO consultorias (vendedor_id, status)
                    VALUES (%s, 'ativa') RETURNING id
                """, (vendedor_id,))
                consultoria_id = cur.fetchone()[0]
                conn.commit()
                cur.close()
                close_conn(conn)

                _gerar_msg_inicial(vendedor_id, consultoria_id, get_conn, close_conn)
            except Exception as e:
                print(f"Consultor: erro ao auto-criar consultoria - {e}")
                try:
                    close_conn(conn)
                except Exception:
                    pass
                return RedirectResponse(url="/hub")

        from fastapi.templating import Jinja2Templates
        import os
        templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

        mensagens = _get_mensagens(consultoria_id, get_conn, close_conn)
        nova = _consultoria_e_nova(consultoria_id, get_conn, close_conn)
        status = _get_status_completo(vendedor_id, consultoria_id, get_conn, close_conn)
        return templates.TemplateResponse(request, "consultoria.html", {
            "usuario_nome": usuario_nome or "",
            "modo": "chat",
            "nova": nova,
            "consultoria_id": consultoria_id,
            "mensagens": mensagens,
            "plano": plano,
            "limite": limite,
            "usado": usado,
            "restantes": max(0, limite - usado),
            "status": status,
        })

    @app.get("/consultoria/status")
    def consultoria_status(usuario_id: str = Cookie(None)):
        if not usuario_id:
            return JSONResponse({"erro": "nao logado"}, status_code=401)

        vendedor_id = _get_vendedor_id(usuario_id, get_conn, close_conn)
        if not vendedor_id:
            return JSONResponse({"erro": "vendedor nao encontrado"}, status_code=404)

        consultoria_id = _get_consultoria_ativa(vendedor_id, get_conn, close_conn)
        if not consultoria_id:
            return JSONResponse({"erro": "sem consultoria ativa"}, status_code=404)

        status = _get_status_completo(vendedor_id, consultoria_id, get_conn, close_conn)
        if not status:
            return JSONResponse({"erro": "falha ao montar status"}, status_code=500)

        return JSONResponse({"ok": True, "status": status})

    @app.get("/consultoria/historico")
    def consultoria_historico(usuario_id: str = Cookie(None)):
        if not usuario_id:
            return JSONResponse({"erro": "nao logado"}, status_code=401)

        vendedor_id = _get_vendedor_id(usuario_id, get_conn, close_conn)
        if not vendedor_id:
            return JSONResponse({"erro": "vendedor nao encontrado"}, status_code=404)

        ativa = _get_consultoria_ativa(vendedor_id, get_conn, close_conn)
        itens = _get_historico(vendedor_id, get_conn, close_conn, excluir_id=ativa)
        return JSONResponse({"ok": True, "historico": itens})

    @app.get("/consultoria/historico/{cid}")
    def consultoria_historico_detalhe(cid: int, usuario_id: str = Cookie(None)):
        if not usuario_id:
            return JSONResponse({"erro": "nao logado"}, status_code=401)

        vendedor_id = _get_vendedor_id(usuario_id, get_conn, close_conn)
        if not vendedor_id:
            return JSONResponse({"erro": "vendedor nao encontrado"}, status_code=404)

        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, status, gargalo_detectado, servico_indicado,
                       criado_em, atualizado_em
                FROM consultorias WHERE id = %s AND vendedor_id = %s
            """, (cid, vendedor_id))
            r = cur.fetchone()
            cur.close()
            close_conn(conn)
        except Exception as e:
            print(f"Consultor: erro ao buscar detalhe historico - {e}")
            try:
                close_conn(conn)
            except Exception:
                pass
            return JSONResponse({"erro": "falha ao buscar"}, status_code=500)

        if not r:
            return JSONResponse({"erro": "consultoria nao encontrada"}, status_code=404)

        mensagens = _get_mensagens(cid, get_conn, close_conn)
        passos = _get_passos(cid, get_conn, close_conn)
        servico_raw = (r[3] or "").strip().lower()

        return JSONResponse({
            "ok": True,
            "consultoria": {
                "id": r[0],
                "status": r[1] or "encerrada",
                "gargalo": (r[2] or "").strip(),
                "servico": servico_raw,
                "servico_nome": NOMES_SERVICOS.get(servico_raw, servico_raw or ""),
                "criado_em": r[4].isoformat() if r[4] else None,
                "atualizado_em": r[5].isoformat() if r[5] else None,
                "total_mensagens": len(mensagens),
                "passos": passos,
            },
            "mensagens": mensagens,
        })

    @app.post("/consultoria/passo/{pid}/toggle")
    def consultoria_passo_toggle(pid: int, usuario_id: str = Cookie(None)):
        if not usuario_id:
            return JSONResponse({"erro": "nao logado"}, status_code=401)

        vendedor_id = _get_vendedor_id(usuario_id, get_conn, close_conn)
        if not vendedor_id:
            return JSONResponse({"erro": "vendedor nao encontrado"}, status_code=404)

        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT p.id, p.concluido
                FROM consultoria_passos p
                JOIN consultorias c ON c.id = p.consultoria_id
                WHERE p.id = %s AND c.vendedor_id = %s
            """, (pid, vendedor_id))
            r = cur.fetchone()
            if not r:
                cur.close()
                close_conn(conn)
                return JSONResponse({"erro": "passo nao encontrado"}, status_code=404)

            novo_valor = not bool(r[1])
            if novo_valor:
                cur.execute("""
                    UPDATE consultoria_passos
                    SET concluido = TRUE, concluido_em = NOW()
                    WHERE id = %s
                """, (pid,))
            else:
                cur.execute("""
                    UPDATE consultoria_passos
                    SET concluido = FALSE, concluido_em = NULL
                    WHERE id = %s
                """, (pid,))
            conn.commit()
            cur.close()
            close_conn(conn)
            return JSONResponse({"ok": True, "concluido": novo_valor})
        except Exception as e:
            print(f"Consultor: erro ao toggle passo - {e}")
            try:
                close_conn(conn)
            except Exception:
                pass
            return JSONResponse({"erro": "falha ao atualizar"}, status_code=500)

    @app.post("/consultoria/iniciar")
    def consultoria_iniciar(usuario_id: str = Cookie(None)):
        if not usuario_id:
            return JSONResponse({"erro": "nao logado"}, status_code=401)

        vendedor_id = _get_vendedor_id(usuario_id, get_conn, close_conn)
        if not vendedor_id:
            return JSONResponse({"erro": "vendedor nao encontrado"}, status_code=404)

        existente = _get_consultoria_ativa(vendedor_id, get_conn, close_conn)
        if existente:
            return JSONResponse({"ok": True, "consultoria_id": existente, "reaproveitada": True})

        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO consultorias (vendedor_id, status)
                VALUES (%s, 'ativa') RETURNING id
            """, (vendedor_id,))
            novo_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            close_conn(conn)
        except Exception as e:
            print(f"Consultor: erro ao criar consultoria - {e}")
            try:
                close_conn(conn)
            except Exception:
                pass
            return JSONResponse({"erro": "falha ao criar consultoria"}, status_code=500)

        _gerar_msg_inicial(vendedor_id, novo_id, get_conn, close_conn)
        return JSONResponse({"ok": True, "consultoria_id": novo_id, "reaproveitada": False})

    @app.post("/consultoria/mensagem")
    async def consultoria_mensagem(request: Request, usuario_id: str = Cookie(None)):
        if not usuario_id:
            return JSONResponse({"erro": "nao logado"}, status_code=401)

        vendedor_id = _get_vendedor_id(usuario_id, get_conn, close_conn)
        if not vendedor_id:
            return JSONResponse({"erro": "vendedor nao encontrado"}, status_code=404)

        try:
            body = await request.json()
        except Exception:
            return JSONResponse({"erro": "body invalido"}, status_code=400)

        texto = (body.get("mensagem") or "").strip()
        if not texto:
            return JSONResponse({"erro": "mensagem vazia"}, status_code=400)

        plano = _get_plano(vendedor_id, get_conn, close_conn)
        limite = LIMITES_DIARIOS.get(plano, 5)
        usado = _uso_hoje(vendedor_id, get_conn, close_conn)

        if usado >= limite:
            return JSONResponse({
                "erro": "limite_diario",
                "mensagem": f"Voce atingiu o limite de {limite} interacoes por dia do plano {plano}. Volta amanha ou faz upgrade.",
                "plano": plano,
                "limite": limite,
                "usado": usado,
            }, status_code=429)

        consultoria_id = _get_consultoria_ativa(vendedor_id, get_conn, close_conn)
        if not consultoria_id:
            return JSONResponse({"erro": "nenhuma consultoria ativa. clique em iniciar."}, status_code=400)

        _salvar_mensagem(consultoria_id, "cliente", texto, get_conn, close_conn)

        dossie = montar_dossie(vendedor_id, get_conn, close_conn)
        dossie_txt = formatar_dossie_para_prompt(dossie)

        mensagens = _get_mensagens(consultoria_id, get_conn, close_conn)
        historico_recente = mensagens[-20:]
        historico_txt = formatar_historico(historico_recente[:-1])

        resposta = gerar_resposta_consultor(
            mensagem_usuario=texto,
            dossie_texto=dossie_txt,
            historico_texto=historico_txt,
        )

        resposta = _limpar_unicode(resposta)
        _salvar_mensagem(consultoria_id, "consultor", resposta, get_conn, close_conn)
        _incrementar_uso(vendedor_id, get_conn, close_conn)

        try:
            mensagens_pos = _get_mensagens(consultoria_id, get_conn, close_conn)
            historico_pos = formatar_historico(mensagens_pos[-20:])
            _analisar_e_salvar(vendedor_id, consultoria_id, historico_pos, get_conn, close_conn)
        except Exception as e:
            print(f"Consultor: erro no pos-analise - {e}")

        status = _get_status_completo(vendedor_id, consultoria_id, get_conn, close_conn)

        usado_novo = usado + 1
        return JSONResponse({
            "ok": True,
            "resposta": resposta,
            "usado": usado_novo,
            "limite": limite,
            "restantes": max(0, limite - usado_novo),
            "status": status,
        })

    @app.post("/consultoria/nova")
    def consultoria_nova(usuario_id: str = Cookie(None)):
        if not usuario_id:
            return JSONResponse({"erro": "nao logado"}, status_code=401)

        vendedor_id = _get_vendedor_id(usuario_id, get_conn, close_conn)
        if not vendedor_id:
            return JSONResponse({"erro": "vendedor nao encontrado"}, status_code=404)

        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                UPDATE consultorias SET status = 'encerrada', atualizado_em = NOW()
                WHERE vendedor_id = %s AND status = 'ativa'
            """, (vendedor_id,))
            cur.execute("""
                INSERT INTO consultorias (vendedor_id, status)
                VALUES (%s, 'ativa') RETURNING id
            """, (vendedor_id,))
            novo_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            close_conn(conn)
        except Exception as e:
            print(f"Consultor: erro ao criar nova consultoria - {e}")
            try:
                close_conn(conn)
            except Exception:
                pass
            return JSONResponse({"erro": "falha ao criar nova"}, status_code=500)

        _gerar_msg_inicial(vendedor_id, novo_id, get_conn, close_conn)
        return JSONResponse({"ok": True, "consultoria_id": novo_id})

    @app.get("/consultoria/ping")
    def consultoria_ping():
        return {"status": "ok", "area": "consultoria", "versao": "0.9"}