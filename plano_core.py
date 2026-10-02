# plano_core.py
# M.A Tech — Cerebro do Painel (regras, sync, calculos)
# Nao depende de HTML nem de rotas. So logica.

def _q1(cur, sql, params=None):
    cur.execute(sql, params or ())
    r = cur.fetchone()
    return r[0] if r else None


def _qa(cur, sql, params=None):
    cur.execute(sql, params or ())
    return cur.fetchall()


def coletar_dados_reais(get_conn, close_conn):
    """Le o estado real do SaaS."""
    conn = get_conn()
    cur = conn.cursor()
    d = {}
    try:
        d["total_usuarios"] = _q1(cur, "SELECT COUNT(*) FROM vendedores") or 0
    except Exception:
        d["total_usuarios"] = 0
    try:
        d["clientes_pagantes"] = _q1(cur, "SELECT COUNT(*) FROM vendedores WHERE plano != 'gratis'") or 0
    except Exception:
        d["clientes_pagantes"] = 0
    try:
        d["usuarios_gratis"] = _q1(cur, "SELECT COUNT(*) FROM vendedores WHERE plano = 'gratis'") or 0
    except Exception:
        d["usuarios_gratis"] = 0
    try:
        d["mrr"] = float(_q1(cur, """
            SELECT COALESCE(SUM(valor),0) FROM pagamentos
            WHERE status='pago' AND criado_em >= DATE_TRUNC('month', CURRENT_DATE)
        """) or 0)
    except Exception:
        d["mrr"] = 0.0
    try:
        d["receita_total"] = float(_q1(cur, "SELECT COALESCE(SUM(valor),0) FROM pagamentos WHERE status='pago'") or 0)
    except Exception:
        d["receita_total"] = 0.0
    try:
        d["leads"] = _q1(cur, "SELECT COUNT(*) FROM leads_landing") or 0
    except Exception:
        d["leads"] = 0
    try:
        d["clientes_crm"] = _q1(cur, "SELECT COUNT(*) FROM clientes") or 0
    except Exception:
        d["clientes_crm"] = 0
    try:
        d["atendimentos"] = _q1(cur, "SELECT COUNT(*) FROM atendimentos") or 0
    except Exception:
        d["atendimentos"] = 0
    cur.close()
    close_conn(conn)
    return d


def carregar_dashboard(get_conn, close_conn):
    """Tudo que o dashboard precisa."""
    conn = get_conn()
    cur = conn.cursor()
    d = {}

    try:
        cur.execute("SELECT * FROM strategic_plans ORDER BY id LIMIT 1")
        cols = [c[0] for c in cur.description]
        r = cur.fetchone()
        d["plano"] = dict(zip(cols, r)) if r else None
    except Exception:
        d["plano"] = None

    try:
        cur.execute("SELECT * FROM roadmap_phases WHERE status='em_execucao' ORDER BY numero LIMIT 1")
        cols = [c[0] for c in cur.description]
        r = cur.fetchone()
        d["fase_atual"] = dict(zip(cols, r)) if r else None
    except Exception:
        d["fase_atual"] = None

    try:
        cur.execute("SELECT * FROM goals WHERE status='em_andamento' ORDER BY id LIMIT 1")
        cols = [c[0] for c in cur.description]
        r = cur.fetchone()
        d["meta_atual"] = dict(zip(cols, r)) if r else None
    except Exception:
        d["meta_atual"] = None

    try:
        cur.execute("""
            SELECT t.*, g.titulo as goal_titulo
            FROM tasks t LEFT JOIN goals g ON g.id=t.goal_id
            WHERE t.status IN ('pendente','em_andamento')
            ORDER BY CASE t.prioridade WHEN 'critica' THEN 1 WHEN 'alta' THEN 2 WHEN 'media' THEN 3 ELSE 4 END, t.id
            LIMIT 1
        """)
        cols = [c[0] for c in cur.description]
        r = cur.fetchone()
        d["proxima_acao"] = dict(zip(cols, r)) if r else None
    except Exception:
        d["proxima_acao"] = None

    try:
        cur.execute("SELECT * FROM blockers WHERE status='aberto' ORDER BY CASE prioridade WHEN 'critica' THEN 1 WHEN 'alta' THEN 2 ELSE 3 END LIMIT 1")
        cols = [c[0] for c in cur.description]
        r = cur.fetchone()
        d["bloqueio_principal"] = dict(zip(cols, r)) if r else None
    except Exception:
        d["bloqueio_principal"] = None

    try:
        d["total_bloqueios"] = _q1(cur, "SELECT COUNT(*) FROM blockers WHERE status='aberto'") or 0
    except Exception:
        d["total_bloqueios"] = 0

    try:
        cur.execute("SELECT COUNT(*) FROM roadmap_phases")
        d["total_fases"] = cur.fetchone()[0] or 9
    except Exception:
        d["total_fases"] = 9

    try:
        cur.execute("SELECT COUNT(*) FROM roadmap_phases WHERE status IN ('concluido','validado')")
        d["fases_concluidas"] = cur.fetchone()[0] or 0
    except Exception:
        d["fases_concluidas"] = 0

    try:
        cur.execute("SELECT COUNT(*) FROM tasks")
        d["total_tarefas"] = cur.fetchone()[0] or 0
    except Exception:
        d["total_tarefas"] = 0

    try:
        cur.execute("SELECT COUNT(*) FROM tasks WHERE status='concluida'")
        d["tarefas_concluidas"] = cur.fetchone()[0] or 0
    except Exception:
        d["tarefas_concluidas"] = 0

    cur.close()
    close_conn(conn)

    # Junta dados reais do SaaS
    d.update(coletar_dados_reais(get_conn, close_conn))

    # Progresso da meta atual
    if d["meta_atual"]:
        try:
            va = float(d["meta_atual"]["valor_atual"] or 0)
            vm = float(d["meta_atual"]["valor_meta"] or 1)
            d["meta_pct"] = int((va / vm) * 100) if vm else 0
        except Exception:
            d["meta_pct"] = 0
    else:
        d["meta_pct"] = 0

    return d


def calcular_execucao(d):
    """Calcula o % de execucao do plano com base em varios fatores."""
    fases_pct = 0
    if d.get("total_fases"):
        fases_pct = int((d.get("fases_concluidas", 0) / d["total_fases"]) * 100)

    tarefas_pct = 0
    if d.get("total_tarefas"):
        tarefas_pct = int((d.get("tarefas_concluidas", 0) / d["total_tarefas"]) * 100)

    meta_pct = d.get("meta_pct", 0)

    base = int((fases_pct * 0.4) + (tarefas_pct * 0.3) + (meta_pct * 0.3))

    bloqueios = d.get("total_bloqueios", 0)

    if bloqueios >= 3:
        status = "atrasado"
        motivo = f"Existem {bloqueios} bloqueios abertos travando o avanco."
    elif bloqueios == 2:
        status = "atencao"
        motivo = f"2 bloqueios abertos. Resolver antes de avancar."
    elif bloqueios == 1:
        status = "atencao"
        motivo = f"1 bloqueio aberto. Monitorar."
    elif base >= 60:
        status = "no_caminho"
        motivo = "Roadmap, tarefas e metas avancando conforme o planejado."
    elif base >= 25:
        status = "atencao"
        motivo = "Avanco abaixo do esperado. Priorizar o que gera resultado."
    else:
        status = "atrasado"
        motivo = "Execucao muito baixa. Focar na proxima acao."

    return {
        "pct": base,
        "fases_pct": fases_pct,
        "tarefas_pct": tarefas_pct,
        "meta_pct": meta_pct,
        "status": status,
        "motivo": motivo,
    }


def executar_sync(get_conn, close_conn):
    """Le o sistema e atualiza o plano automaticamente. Retorna resumo."""
    resultado = {
        "tarefas_concluidas": [],
        "metas_atualizadas": [],
        "fases_atualizadas": [],
        "mensagem": "",
    }

    d = coletar_dados_reais(get_conn, close_conn)

    conn = get_conn()
    cur = conn.cursor()

    # 1. Atualiza meta dos clientes
    try:
        cur.execute("SELECT id, valor_meta FROM goals WHERE titulo LIKE '%primeiros 5%' LIMIT 1")
        r = cur.fetchone()
        if r:
            gid, vmeta = r
            atual = d["clientes_pagantes"]
            novo_status = "validado" if atual >= (vmeta or 5) else ("em_andamento" if atual > 0 else "nao_iniciado")
            cur.execute("UPDATE goals SET valor_atual=%s, status=%s, atualizado_em=NOW() WHERE id=%s",
                        (atual, novo_status, gid))
            resultado["metas_atualizadas"].append({"meta": "5 clientes", "valor": atual, "status": novo_status})
    except Exception as e:
        pass

    # 2. Meta 10 clientes
    try:
        cur.execute("SELECT id, valor_meta FROM goals WHERE titulo LIKE '%10 clientes%' LIMIT 1")
        r = cur.fetchone()
        if r:
            gid, vmeta = r
            atual = d["clientes_pagantes"]
            novo_status = "validado" if atual >= (vmeta or 10) else ("em_andamento" if atual >= 5 else "nao_iniciado")
            cur.execute("UPDATE goals SET valor_atual=%s, status=%s, atualizado_em=NOW() WHERE id=%s",
                        (atual, novo_status, gid))
            resultado["metas_atualizadas"].append({"meta": "10 clientes", "valor": atual, "status": novo_status})
    except Exception:
        pass

    # 3. Marca tarefas concluidas conforme dados reais
    try:
        if d["total_usuarios"] > 0:
            cur.execute("""UPDATE tasks SET status='concluida', concluida_em=NOW(), atualizado_em=NOW()
                WHERE LOWER(titulo) LIKE '%usuarios%' AND status != 'concluida'""")
            if cur.rowcount > 0:
                resultado["tarefas_concluidas"].append(f"{cur.rowcount} tarefas de usuarios")
        if d["leads"] > 0:
            cur.execute("""UPDATE tasks SET status='concluida', concluida_em=NOW(), atualizado_em=NOW()
                WHERE LOWER(titulo) LIKE '%contato%' AND status != 'concluida'""")
            if cur.rowcount > 0:
                resultado["tarefas_concluidas"].append(f"{cur.rowcount} tarefas de contato")
        if d["clientes_pagantes"] > 0:
            cur.execute("""UPDATE tasks SET status='concluida', concluida_em=NOW(), atualizado_em=NOW()
                WHERE LOWER(titulo) LIKE '%primeiro cliente%' AND status != 'concluida'""")
            if cur.rowcount > 0:
                resultado["tarefas_concluidas"].append(f"{cur.rowcount} tarefas de cliente")
    except Exception:
        pass

    # 4. Avanca fase 1 automaticamente se as rotas existem
    try:
        cur.execute("SELECT id, status FROM roadmap_phases WHERE numero=1")
        r = cur.fetchone()
        if r and r[1] != "concluido":
            cur.execute("UPDATE roadmap_phases SET status='concluido', percentual=100, atualizado_em=NOW() WHERE numero=1")
            resultado["fases_atualizadas"].append("Fase 1 concluida")
    except Exception:
        pass

    # 5. Registra no diario apenas se houver mudanca
    total_mudancas = len(resultado["tarefas_concluidas"]) + len(resultado["metas_atualizadas"]) + len(resultado["fases_atualizadas"])
    if total_mudancas > 0:
        try:
            resumo = f"Tarefas: {len(resultado['tarefas_concluidas'])}. "
            resumo += f"Metas: {len(resultado['metas_atualizadas'])}. "
            resumo += f"Fases: {len(resultado['fases_atualizadas'])}."
            cur.execute("""INSERT INTO journal_entries (titulo, conteudo, categoria, resultado)
                VALUES (%s, %s, %s, %s)""",
                ("Sync executado", resumo, "produto", "OK"))
        except Exception:
            pass

    conn.commit()
    cur.close()
    close_conn(conn)

    resultado["mensagem"] = f"{total_mudancas} atualizacoes aplicadas"
    return resultado