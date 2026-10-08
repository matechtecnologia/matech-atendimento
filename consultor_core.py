# consultor_core.py
# M.A Tech — Nucleo da Consultoria Empresarial
# Monta o dossie do vendedor: tudo que a IA precisa saber antes
# de comecar a conversa.
#
# Funcao principal: montar_dossie(vendedor_id, get_conn, close_conn)
# Retorna um dict com 11 dados. A IA recebe isso como contexto.


def _contar(cur, sql, params=()):
    """Helper: roda um SELECT que retorna 1 numero e devolve int."""
    cur.execute(sql, params)
    r = cur.fetchone()
    return int(r[0]) if r and r[0] is not None else 0


def _buscar_um(cur, sql, params=()):
    """Helper: roda um SELECT que retorna 1 linha e devolve a linha ou None."""
    cur.execute(sql, params)
    return cur.fetchone()


def montar_dossie(vendedor_id, get_conn, close_conn):
    """Le o banco e devolve um dict com tudo que a IA precisa saber
    sobre o vendedor. Nunca lanca excecao — se algo falhar, devolve
    o valor padrao (0, lista vazia, etc) pra nao travar a consultoria."""

    dossie = {
        "total_clientes": 0,
        "clientes_por_status": {},
        "total_atendimentos": 0,
        "atendimentos_sem_resposta": 0,
        "followups_pendentes": 0,
        "followups_atrasados": 0,
        "nichos": [],
        "uso_ia_mes": 0,
        "limite_plano": 300,
        "percentual_plano": 0,
        "dias_desde_ultimo_atendimento": None,
        "plano": "gratis",
        "plano_expira_em": None,
    }

    try:
        conn = get_conn()
        cur = conn.cursor()

        # -------------------------------------------------------
        # 1. TOTAL DE CLIENTES
        # -------------------------------------------------------
        dossie["total_clientes"] = _contar(
            cur,
            "SELECT COUNT(*) FROM clientes WHERE vendedor_id = %s",
            (vendedor_id,)
        )

        # -------------------------------------------------------
        # 2. CLIENTES POR STATUS
        # -------------------------------------------------------
        cur.execute("""
            SELECT LOWER(COALESCE(status, 'novo lead')) AS s, COUNT(*)
            FROM clientes
            WHERE vendedor_id = %s
            GROUP BY LOWER(COALESCE(status, 'novo lead'))
        """, (vendedor_id,))
        por_status = {}
        for status, qtd in cur.fetchall():
            # Normaliza variacoes (mesma logica do app.py linha 1542+)
            if status in ("lead",):
                status = "novo lead"
            elif status in ("negociacao", "negociação"):
                status = "negociando"
            por_status[status] = int(qtd)
        dossie["clientes_por_status"] = por_status

        # -------------------------------------------------------
        # 3. TOTAL DE ATENDIMENTOS
        # -------------------------------------------------------
        dossie["total_atendimentos"] = _contar(
            cur,
            "SELECT COUNT(*) FROM atendimentos WHERE atendente_id = %s",
            (vendedor_id,)
        )

        # -------------------------------------------------------
        # 4. ATENDIMENTOS SEM RESPOSTA (status != 'pronto')
        # -------------------------------------------------------
        dossie["atendimentos_sem_resposta"] = _contar(
            cur,
            """SELECT COUNT(*) FROM atendimentos
               WHERE atendente_id = %s
                 AND (status IS NULL OR status != 'pronto')""",
            (vendedor_id,)
        )

        # -------------------------------------------------------
        # 5/6. FOLLOW-UPS (regra do DOC 10)
        # PENDENTE = cliente cujo ultimo contato passou do prazo do status
        # ATRASADO = pendente E prazo ja venceu (dias_diff < 0)
        # -------------------------------------------------------
        # Prazos por status (dias sem contato)
        prazos = {
            "novo lead": 1,
            "em atendimento": 2,
            "negociando": 2,
            "cliente": 15,
            # perdido: nao mostra
        }

        cur.execute("""
            SELECT
                LOWER(COALESCE(c.status, 'novo lead')) AS status,
                COALESCE(
                    (SELECT MAX(criado_em) FROM atendimentos a
                     WHERE a.cliente_id = c.id),
                    c.criado_em
                ) AS ultimo_contato
            FROM clientes c
            WHERE c.vendedor_id = %s
        """, (vendedor_id,))

        from datetime import datetime, timezone
        agora = datetime.now(timezone.utc)

        pendentes = 0
        atrasados = 0

        for row in cur.fetchall():
            status, ultimo = row[0], row[1]
            if status in ("lead",):
                status = "novo lead"
            elif status in ("negociacao", "negociação"):
                status = "negociando"

            if status == "perdido" or status not in prazos:
                continue

            if ultimo is None:
                continue

            # Garantir timezone
            if ultimo.tzinfo is None:
                ultimo = ultimo.replace(tzinfo=timezone.utc)

            dias_sem_contato = (agora - ultimo).days
            prazo = prazos[status]

            if dias_sem_contato >= prazo:
                pendentes += 1
                if dias_sem_contato > prazo:
                    atrasados += 1

        dossie["followups_pendentes"] = pendentes
        dossie["followups_atrasados"] = atrasados

        # -------------------------------------------------------
        # 7. NICHOS CADASTRADOS
        # -------------------------------------------------------
        cur.execute("""
            SELECT nome FROM nichos
            WHERE vendedor_id = %s AND COALESCE(ativo, TRUE) = TRUE
            ORDER BY id
        """, (vendedor_id,))
        dossie["nichos"] = [r[0] for r in cur.fetchall() if r[0]]

        # -------------------------------------------------------
        # 7b. NICHO COMPLETO (com dados do onboarding)
        # -------------------------------------------------------
        cur.execute("""
            SELECT nome, produto, publico, preco, dor, objecao, diferencial, tom
            FROM nichos
            WHERE vendedor_id = %s AND COALESCE(ativo, TRUE) = TRUE
            ORDER BY id
        """, (vendedor_id,))
        _todos_nichos = []
        for _n in cur.fetchall():
            _todos_nichos.append({
                "nome": _n[0] or "",
                "produto": _n[1] or "",
                "publico": _n[2] or "",
                "preco": _n[3] or "",
                "dor": _n[4] or "",
                "objecao": _n[5] or "",
                "diferencial": _n[6] or "",
                "tom": _n[7] or "",
            })
        dossie["nichos_detalhados"] = _todos_nichos
        dossie["nicho_detalhado"] = _todos_nichos[0] if _todos_nichos else None

        # -------------------------------------------------------
        # 7c. CLIENTES CONCRETOS (nomes + status + tempo sem contato)
        # -------------------------------------------------------
        cur.execute("""
            SELECT nome, COALESCE(status, 'novo lead') AS status, criado_em
            FROM clientes
            WHERE vendedor_id = %s
            ORDER BY id DESC LIMIT 10
        """, (vendedor_id,))
        _cs = []
        for _c in cur.fetchall():
            _cs.append({
                "nome": _c[0] or "(sem nome)",
                "status": _c[1] or "novo lead",
                "criado_em": _c[2].isoformat() if _c[2] else None,
            })
        dossie["clientes_detalhados"] = _cs

        # -------------------------------------------------------
        # 8. USO DE IA NO MES (respostas_ia)
        # -------------------------------------------------------
        mes_ano = datetime.now().strftime("%Y-%m")
        dossie["uso_ia_mes"] = _contar(
            cur,
            """SELECT COALESCE(total, 0) FROM respostas_ia
               WHERE vendedor_id = %s AND mes_ano = %s""",
            (vendedor_id, mes_ano)
        )

        # -------------------------------------------------------
        # 9/13. PLANO + LIMITE + EXPIRACAO
        # -------------------------------------------------------
        limite_por_plano = {
            "gratis": 300,
            "basico": 3000,
            "pro": 10000,
            "empresarial": 30000,
        }

        row = _buscar_um(
            cur,
            "SELECT plano, plano_expira_em FROM vendedores WHERE id = %s",
            (vendedor_id,)
        )
        if row:
            plano = (row[0] or "gratis").lower()
            dossie["plano"] = plano
            dossie["limite_plano"] = limite_por_plano.get(plano, 300)
            dossie["plano_expira_em"] = row[1].isoformat() if row[1] else None

        # -------------------------------------------------------
        # 10. PERCENTUAL DO PLANO USADO
        # -------------------------------------------------------
        if dossie["limite_plano"] > 0:
            pct = int((dossie["uso_ia_mes"] / dossie["limite_plano"]) * 100)
            dossie["percentual_plano"] = min(pct, 999)

        # -------------------------------------------------------
        # 11. DIAS DESDE ULTIMO ATENDIMENTO
        # -------------------------------------------------------
        cur.execute("""
            SELECT MAX(criado_em) FROM atendimentos
            WHERE atendente_id = %s
        """, (vendedor_id,))
        row = cur.fetchone()
        ultimo_at = row[0] if row else None

        if ultimo_at:
            if ultimo_at.tzinfo is None:
                ultimo_at = ultimo_at.replace(tzinfo=timezone.utc)
            dossie["dias_desde_ultimo_atendimento"] = (agora - ultimo_at).days

        cur.close()
        close_conn(conn)

    except Exception as e:
        # Nunca deixa a consultoria quebrar por causa do dossie.
        # Se algo falhar, devolve o que ja tinha (defaults).
        print(f"Consultor Core: erro ao montar dossie - {e}")
        try:
            close_conn(conn)
        except Exception:
            pass

    return dossie


def formatar_dossie_para_prompt(dossie):
    """Transforma o dict do dossie em texto legivel pra IA ler.
    A IA vai receber isso no inicio do system prompt."""

    linhas = ["=== DOSSIE DO VENDEDOR ==="]

    linhas.append(f"Plano atual: {dossie.get('plano', 'gratis')}")
    if dossie.get("plano_expira_em"):
        linhas.append(f"Plano expira em: {dossie['plano_expira_em']}")

    linhas.append(f"Total de clientes cadastrados: {dossie.get('total_clientes', 0)}")

    por_status = dossie.get("clientes_por_status", {})
    if por_status:
        detalhe = ", ".join(f"{k}: {v}" for k, v in sorted(por_status.items()))
        linhas.append(f"Clientes por status: {detalhe}")

    linhas.append(f"Total de atendimentos feitos: {dossie.get('total_atendimentos', 0)}")
    linhas.append(f"Atendimentos sem resposta: {dossie.get('atendimentos_sem_resposta', 0)}")
    linhas.append(f"Follow-ups pendentes: {dossie.get('followups_pendentes', 0)}")
    linhas.append(f"Follow-ups atrasados: {dossie.get('followups_atrasados', 0)}")

    nichos = dossie.get("nichos", [])
    if nichos:
        linhas.append(f"Nichos cadastrados: {', '.join(nichos)}")
    else:
        linhas.append("Nichos cadastrados: nenhum ainda")

    uso = dossie.get("uso_ia_mes", 0)
    limite = dossie.get("limite_plano", 0)
    pct = dossie.get("percentual_plano", 0)
    linhas.append(f"Uso de IA no mes: {uso} de {limite} respostas ({pct}%)")

    dias = dossie.get("dias_desde_ultimo_atendimento")
    if dias is not None:
        linhas.append(f"Dias desde o ultimo atendimento: {dias}")
    else:
        linhas.append("Dias desde o ultimo atendimento: nunca atendeu")

    # Nichos detalhados (todos)
    todos = dossie.get("nichos_detalhados", [])
    if todos:
        linhas.append("")
        linhas.append(f"--- NICHOS CONFIGURADOS ({len(todos)} cadastrado(s)) ---")
        for idx, nd in enumerate(todos, 1):
            linhas.append(f"")
            linhas.append(f"NICHO {idx}:")
            if nd.get("nome"): linhas.append(f"  Nome: {nd['nome']}")
            if nd.get("produto"): linhas.append(f"  O que vende: {nd['produto']}")
            if nd.get("publico"): linhas.append(f"  Para quem vende: {nd['publico']}")
            if nd.get("preco"): linhas.append(f"  Preco: {nd['preco']}")
            if nd.get("dor"): linhas.append(f"  Dor do cliente final: {nd['dor']}")
            if nd.get("objecao"): linhas.append(f"  Objecao comum: {nd['objecao']}")
            if nd.get("diferencial"): linhas.append(f"  Diferencial: {nd['diferencial']}")
            if nd.get("tom"): linhas.append(f"  Tom de voz: {nd['tom']}")
        linhas.append("")
        linhas.append("--- FIM DOS NICHOS ---")
    else:
        linhas.append("")
        linhas.append("NICHO: ainda nao configurado (o dono nao fez onboarding completo)")

    # Clientes concretos
    cd = dossie.get("clientes_detalhados", [])
    if cd:
        linhas.append("")
        linhas.append("--- ULTIMOS CLIENTES CADASTRADOS ---")
        for cli in cd[:10]:
            linhas.append(f"- {cli['nome']} (status: {cli['status']})")
        linhas.append("--- FIM DOS CLIENTES ---")

    linhas.append("=== FIM DO DOSSIE ===")
    return "\n".join(linhas)