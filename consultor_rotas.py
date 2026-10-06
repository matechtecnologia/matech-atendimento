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
# LIMPEZA DE UNICODE (mesmo bug do gemini.py)
# ============================================================
def _limpar_unicode(texto):
    """Remove caracteres unicode invisiveis que quebram copy/paste
    no WhatsApp e em outros apps (mesmo problema do \\u202f nos precos)."""
    if not texto:
        return texto
    problematicos = {
        "\u202f": " ",  # narrow no-break space
        "\u00a0": " ",  # no-break space
        "\u2009": " ",  # thin space
        "\u200a": " ",  # hair space
        "\u200b": "",   # zero-width space
        "\u200c": "",   # zero-width non-joiner
        "\u200d": "",   # zero-width joiner
        "\ufeff": "",   # BOM
    }
    for antigo, novo in problematicos.items():
        texto = texto.replace(antigo, novo)
    return texto


# ============================================================
# HELPERS INTERNOS
# ============================================================
def _get_vendedor_id(usuario_id, get_conn, close_conn):
    """Converte usuario_id -> vendedor_id. Mesmo padrao do app.py:717."""
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
    """Retorna o plano do vendedor (lowercase). Default: gratis."""
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
    """Retorna quantas interacoes o vendedor ja usou hoje."""
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
    """Soma +1 no uso de hoje (cria a linha se nao existir)."""
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
    """Retorna o id da consultoria ativa (ou None)."""
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
    """Retorna lista de mensagens da consultoria, em ordem cronologica."""
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
    """Salva 1 mensagem (consultor ou cliente)."""
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
    """Retorna True se a consultoria foi criada nos ultimos 60 segundos.
    Usado pra mostrar o separador 'Nova consultoria iniciada' no chat."""
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
    """Gera a 1a mensagem da IA ao criar uma consultoria.
    NAO conta no limite diario. Se falhar, nao quebra o fluxo."""
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
# REGISTRO DAS ROTAS
# ============================================================
def registrar_rotas_consultor(app, get_conn, close_conn, Cookie, Request):

    from consultor_core import montar_dossie, formatar_dossie_para_prompt
    from consultor import gerar_resposta_consultor, formatar_historico

    # --------------------------------------------------------
    # GET /consultoria — tela inicial
    # Decide se mostra botao "iniciar" ou chat existente
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

        from fastapi.templating import Jinja2Templates
        import os
        templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

        # Se nao tem consultoria ativa, mostra tela de boas-vindas
        if not consultoria_id:
            return templates.TemplateResponse(request, "consultoria.html", {
                "usuario_nome": usuario_nome or "",
                "modo": "inicio",
                "plano": plano,
                "limite": limite,
                "usado": usado,
                "restantes": max(0, limite - usado),
            })

        # Se tem, carrega o chat com o historico
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
    # POST /consultoria/iniciar — cria consultoria nova
    # Tambem gera a 1a mensagem da IA (nao conta no limite)
    # --------------------------------------------------------
    @app.post("/consultoria/iniciar")
    def consultoria_iniciar(usuario_id: str = Cookie(None)):
        if not usuario_id:
            return JSONResponse({"erro": "nao logado"}, status_code=401)

        vendedor_id = _get_vendedor_id(usuario_id, get_conn, close_conn)
        if not vendedor_id:
            return JSONResponse({"erro": "vendedor nao encontrado"}, status_code=404)

        # Ja tem uma ativa? Retorna ela (nao gera msg nova).
        existente = _get_consultoria_ativa(vendedor_id, get_conn, close_conn)
        if existente:
            return JSONResponse({"ok": True, "consultoria_id": existente, "reaproveitada": True})

        # Cria nova
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

        # Gera a 1a mensagem da IA
        _gerar_msg_inicial(vendedor_id, novo_id, get_conn, close_conn)

        return JSONResponse({"ok": True, "consultoria_id": novo_id, "reaproveitada": False})

    # --------------------------------------------------------
    # POST /consultoria/mensagem — envia msg e recebe resposta
    # --------------------------------------------------------
    @app.post("/consultoria/mensagem")
    async def consultoria_mensagem(request: Request, usuario_id: str = Cookie(None)):
        if not usuario_id:
            return JSONResponse({"erro": "nao logado"}, status_code=401)

        vendedor_id = _get_vendedor_id(usuario_id, get_conn, close_conn)
        if not vendedor_id:
            return JSONResponse({"erro": "vendedor nao encontrado"}, status_code=404)

        # Le JSON do body
        try:
            body = await request.json()
        except Exception:
            return JSONResponse({"erro": "body invalido"}, status_code=400)

        texto = (body.get("mensagem") or "").strip()
        if not texto:
            return JSONResponse({"erro": "mensagem vazia"}, status_code=400)

        # Verifica limite diario
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

        # Pega consultoria ativa (cria se nao existir)
        consultoria_id = _get_consultoria_ativa(vendedor_id, get_conn, close_conn)
        if not consultoria_id:
            return JSONResponse({"erro": "nenhuma consultoria ativa. clique em iniciar."}, status_code=400)

        # Salva mensagem do cliente
        _salvar_mensagem(consultoria_id, "cliente", texto, get_conn, close_conn)

        # Monta o dossie
        dossie = montar_dossie(vendedor_id, get_conn, close_conn)
        dossie_txt = formatar_dossie_para_prompt(dossie)

        # Pega historico (ultimas 20)
        mensagens = _get_mensagens(consultoria_id, get_conn, close_conn)
        historico_recente = mensagens[-20:]
        historico_txt = formatar_historico(historico_recente[:-1])  # tudo menos a que acabou de salvar

        # Chama a IA
        resposta = gerar_resposta_consultor(
            mensagem_usuario=texto,
            dossie_texto=dossie_txt,
            historico_texto=historico_txt,
        )

        # Limpa unicode problematico
        resposta = _limpar_unicode(resposta)

        # Salva a resposta
        _salvar_mensagem(consultoria_id, "consultor", resposta, get_conn, close_conn)

        # Incrementa o uso do dia
        _incrementar_uso(vendedor_id, get_conn, close_conn)

        usado_novo = usado + 1
        return JSONResponse({
            "ok": True,
            "resposta": resposta,
            "usado": usado_novo,
            "limite": limite,
            "restantes": max(0, limite - usado_novo),
        })

    # --------------------------------------------------------
    # POST /consultoria/nova — encerra atual e comeca outra
    # Tambem gera a 1a mensagem da IA (nao conta no limite)
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
            # Encerra todas as ativas
            cur.execute("""
                UPDATE consultorias SET status = 'encerrada', atualizado_em = NOW()
                WHERE vendedor_id = %s AND status = 'ativa'
            """, (vendedor_id,))
            # Cria nova
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

        # Gera a 1a mensagem da IA
        _gerar_msg_inicial(vendedor_id, novo_id, get_conn, close_conn)

        return JSONResponse({"ok": True, "consultoria_id": novo_id})

    # --------------------------------------------------------
    # GET /consultoria/ping — mantido pra debug
    # --------------------------------------------------------
    @app.get("/consultoria/ping")
    def consultoria_ping():
        return {"status": "ok", "area": "consultoria", "versao": "0.3"}