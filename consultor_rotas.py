# consultor_rotas.py
# M.A Tech — Rotas da Consultoria Empresarial
# API JSON + tela inicial.
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
# ETAPA 3 — ANALISE AUTOMATICA (2a chamada de IA)
# ============================================================
def _analisar_e_salvar(vendedor_id, consultoria_id, historico_txt, get_conn, close_conn):
    """Faz uma 2a chamada curta ao Groq pra extrair gargalo + servico
    da conversa. Salva em consultorias se detectar. Nao quebra o fluxo
    se falhar."""
    try:
        from groq import Groq
        import os as _os
        import json as _json
        import re as _re

        api_key = _os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Consultor: GROQ_API_KEY ausente na analise.")
            return

        # Se ja tem gargalo salvo, nao refaz (otimizacao)
        try:
            _c = get_conn()
            _cu = _c.cursor()
            _cu.execute("SELECT gargalo_detectado, servico_indicado FROM consultorias WHERE id = %s", (consultoria_id,))
            _r = _cu.fetchone()
            _cu.close()
            close_conn(_c)
            if _r and _r[0] and _r[1]:
                print(f"Consultor: analise pulada (consultoria #{consultoria_id} ja tem gargalo+servico).")
                return
        except Exception:
            try:
                close_conn(_c)
            except Exception:
                pass

        prompt = f"""Analise a conversa abaixo entre um CONSULTOR da M.A Tech e um VENDEDOR.

Sua tarefa: extrair 2 informacoes em formato JSON.
Se ainda nao houver informacao suficiente, retorne null nos campos.

- "gargalo": o problema principal do negocio do vendedor (frase curta, ate 60 chars)
- "servico": qual servico M.A Tech o consultor indicou ou esta indicando
  (valores aceitos: "atendimento_ia", "gestao", "trafego", "crm", "automacao", "nenhum")

Responda APENAS com JSON valido, sem texto extra, sem crase, sem markdown.

Formato exato:
{{"gargalo": "...", "servico": "..."}}

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
        print(f"Consultor: resposta bruta da 2a chamada = {conteudo[:200]!r}")

        # Extrai JSON com regex (defensivo)
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

        # Valida servico
        validos = {"atendimento_ia", "gestao", "trafego", "crm", "automacao"}
        if servico not in validos:
            servico = None

        if gargalo:
            gargalo = _limpar_unicode(gargalo)[:200]
        if not gargalo and not servico:
            print("Consultor: nada util pra salvar (gargalo e servico vazios).")
            return

        # Salva no banco (so o que foi detectado, sem sobrescrever o que ja existe)
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

    # --------------------------------------------------------
    # GET /consultoria — abre direto o chat (auto-cria se nao existir)
    # --------------------------------------------------------
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
        })

    # --------------------------------------------------------
    # POST /consultoria/iniciar
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # POST /consultoria/mensagem
    # --------------------------------------------------------
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

        # ETAPA 3: 2a chamada pra extrair gargalo + servico
        try:
            mensagens_pos = _get_mensagens(consultoria_id, get_conn, close_conn)
            historico_pos = formatar_historico(mensagens_pos[-20:])
            _analisar_e_salvar(vendedor_id, consultoria_id, historico_pos, get_conn, close_conn)
        except Exception as e:
            print(f"Consultor: erro no pos-analise - {e}")

        usado_novo = usado + 1
        return JSONResponse({
            "ok": True,
            "resposta": resposta,
            "usado": usado_novo,
            "limite": limite,
            "restantes": max(0, limite - usado_novo),
        })

    # --------------------------------------------------------
    # POST /consultoria/nova
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # GET /consultoria/ping
    # --------------------------------------------------------
    @app.get("/consultoria/ping")
    def consultoria_ping():
        return {"status": "ok", "area": "consultoria", "versao": "0.5"}