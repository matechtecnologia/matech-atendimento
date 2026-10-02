# plano_sync.py
# M.A Tech — Motor de auto-sync
# Le o estado do sistema (banco + arquivos) e atualiza o plano sozinho
# Criado em: 01/10/2026

import os
import glob


def _rota_existe(app, rota):
    try:
        for r in app.routes:
            if getattr(r, "path", None) == rota:
                return True
    except Exception:
        pass
    return False


def _contar_rotas_plano(app):
    total = 0
    try:
        for r in app.routes:
            p = getattr(r, "path", "") or ""
            if p.startswith("/plano"):
                total += 1
    except Exception:
        pass
    return total


def _contar_tabelas_plano(get_conn, close_conn):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema='public' AND table_name IN (
                'strategic_plans','roadmap_phases','goals','tasks',
                'projects','products','metrics','decisions','blockers',
                'journal_entries','weekly_reports','monthly_reports',
                'revenue_records','plan_modules'
            )
        """)
        n = cur.fetchone()[0]
    except Exception:
        n = 0
    cur.close()
    close_conn(conn)
    return n


def _dados_reais(get_conn, close_conn):
    conn = get_conn()
    cur = conn.cursor()
    d = {}
    try:
        cur.execute("SELECT COUNT(*) FROM vendedores")
        d["total_usuarios"] = cur.fetchone()[0]
    except Exception:
        d["total_usuarios"] = 0
    try:
        cur.execute("SELECT COUNT(*) FROM vendedores WHERE plano != 'gratis'")
        d["clientes_pagantes"] = cur.fetchone()[0]
    except Exception:
        d["clientes_pagantes"] = 0
    try:
        cur.execute("""
            SELECT COALESCE(SUM(valor),0) FROM pagamentos
            WHERE status='pago'
        """)
        d["receita_total"] = float(cur.fetchone()[0] or 0)
    except Exception:
        d["receita_total"] = 0.0
    try:
        cur.execute("SELECT COUNT(*) FROM leads_landing")
        d["leads"] = cur.fetchone()[0]
    except Exception:
        d["leads"] = 0
    try:
        cur.execute("SELECT COUNT(*) FROM clientes")
        d["clientes_no_crm"] = cur.fetchone()[0]
    except Exception:
        d["clientes_no_crm"] = 0
    try:
        cur.execute("SELECT COUNT(*) FROM atendimentos")
        d["atendimentos"] = cur.fetchone()[0]
    except Exception:
        d["atendimentos"] = 0
    try:
        cur.execute("SELECT COUNT(*) FROM produtos" if False else "SELECT 1")
        cur.fetchone()
    except Exception:
        pass
    cur.close()
    close_conn(conn)
    return d


def _registrar_diario(get_conn, close_conn, titulo, conteudo, categoria, resultado=""):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO journal_entries (titulo, conteudo, categoria, resultado)
            VALUES (%s, %s, %s, %s)
        """, (titulo, conteudo, categoria, resultado))
        conn.commit()
        cur.close()
        close_conn(conn)
    except Exception:
        pass


def _marcar_tarefa_concluida(get_conn, close_conn, palavras_chave):
    """Marca a tarefa mais antiga pendente cujo titulo contenha alguma palavra-chave."""
    if not palavras_chave:
        return False
    try:
        conn = get_conn()
        cur = conn.cursor()
        for palavra in palavras_chave:
            cur.execute("""
                SELECT id, titulo FROM tasks
                WHERE status IN ('pendente','em_andamento')
                  AND LOWER(titulo) LIKE %s
                ORDER BY id
                LIMIT 1
            """, (f"%{palavra.lower()}%",))
            row = cur.fetchone()
            if row:
                tid, titulo = row
                cur.execute("""
                    UPDATE tasks SET status='concluida',
                                     concluida_em=CURRENT_TIMESTAMP,
                                     atualizado_em=CURRENT_TIMESTAMP
                    WHERE id=%s
                """, (tid,))
                conn.commit()
                cur.close()
                close_conn(conn)
                return titulo
        cur.close()
        close_conn(conn)
    except Exception:
        pass
    return None


def _criar_tarefa(get_conn, close_conn, titulo, goal_id, prioridade, descricao=""):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id FROM tasks WHERE LOWER(titulo)=LOWER(%s) LIMIT 1", (titulo,))
        if cur.fetchone():
            cur.close()
            close_conn(conn)
            return False
        cur.execute("""
            INSERT INTO tasks (titulo, descricao, goal_id, status, prioridade)
            VALUES (%s, %s, %s, 'pendente', %s)
        """, (titulo, descricao, goal_id, prioridade))
        conn.commit()
        cur.close()
        close_conn(conn)
        return True
    except Exception:
        return False


def _atualizar_meta(get_conn, close_conn, keyword, valor_atual, status=None):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, valor_meta, status FROM goals
            WHERE LOWER(titulo) LIKE %s
            ORDER BY id LIMIT 1
        """, (f"%{keyword.lower()}%",))
        row = cur.fetchone()
        if not row:
            cur.close()
            close_conn(conn)
            return None
        gid, vmeta, st_atual = row
        novo_status = status
        if not novo_status:
            if vmeta and valor_atual >= float(vmeta):
                novo_status = "validado"
            elif valor_atual > 0:
                novo_status = "em_andamento"
            else:
                novo_status = "nao_iniciado"
        cur.execute("""
            UPDATE goals SET valor_atual=%s, status=%s,
                             atualizado_em=CURRENT_TIMESTAMP
            WHERE id=%s
        """, (valor_atual, novo_status, gid))
        conn.commit()
        cur.close()
        close_conn(conn)
        return novo_status
    except Exception:
        return None


def _atualizar_fase(get_conn, close_conn, numero, status=None, percentual=None):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, status, percentual FROM roadmap_phases WHERE numero=%s LIMIT 1", (numero,))
        row = cur.fetchone()
        if not row:
            cur.close()
            close_conn(conn)
            return None
        fid, st_atual, pct_atual = row
        novo_st = status or st_atual
        novo_pct = percentual if percentual is not None else pct_atual
        cur.execute("""
            UPDATE roadmap_phases SET status=%s, percentual=%s,
                                       atualizado_em=CURRENT_TIMESTAMP
            WHERE id=%s
        """, (novo_st, novo_pct, fid))
        conn.commit()
        cur.close()
        close_conn(conn)
        return (novo_st, novo_pct)
    except Exception:
        return None


def _contar_arquivos_py():
    try:
        return len(glob.glob("*.py"))
    except Exception:
        return 0


def executar_sync(app, get_conn, close_conn):
    """Roda todas as regras de auto-sync. Retorna um dict com o resumo."""

    resultado = {
        "tarefas_concluidas": [],
        "tarefas_criadas": [],
        "metas_atualizadas": [],
        "fases_atualizadas": [],
        "erros": [],
    }

    # ---------- REGRAS BASEADAS EM ARQUIVOS ----------
    n_rotas = _contar_rotas_plano(app)
    n_tabelas = _contar_tabelas_plano(get_conn, close_conn)

    # Fase 1 (Atendimento construido) — ja esta 100%
    if n_rotas >= 5 and n_tabelas >= 14:
        r = _atualizar_fase(get_conn, close_conn, 1, "concluido", 100)
        if r:
            resultado["fases_atualizadas"].append({"fase": 1, "resultado": r})

    # Fase 2 (Validacao comercial) — comeca se existir rota /plano
    if n_rotas >= 5:
        r = _atualizar_fase(get_conn, close_conn, 2, "em_execucao", max(10, min(50, n_rotas * 5)))
        if r:
            resultado["fases_atualizadas"].append({"fase": 2, "resultado": r})

    # ---------- REGRAS BASEADAS NO BANCO ----------
    d = _dados_reais(get_conn, close_conn)

    # Meta "5 clientes"
    if d["clientes_pagantes"] > 0:
        r = _atualizar_meta(get_conn, close_conn, "5 clientes", d["clientes_pagantes"])
        if r:
            resultado["metas_atualizadas"].append({"meta": "5 clientes", "valor": d["clientes_pagantes"], "status": r})

    # Meta "10 clientes"
    if d["clientes_pagantes"] >= 5:
        r = _atualizar_meta(get_conn, close_conn, "10 clientes", d["clientes_pagantes"])
        if r:
            resultado["metas_atualizadas"].append({"meta": "10 clientes", "valor": d["clientes_pagantes"], "status": r})

    # Meta "20 clientes"
    if d["clientes_pagantes"] >= 10:
        r = _atualizar_meta(get_conn, close_conn, "20 clientes", d["clientes_pagantes"])
        if r:
            resultado["metas_atualizadas"].append({"meta": "20 clientes", "valor": d["clientes_pagantes"], "status": r})

    # ---------- REGRAS BASEADAS EM DADOS REAIS ----------
    if d["total_usuarios"] > 0:
        t = _marcar_tarefa_concluida(get_conn, close_conn, ["primeiro usu", "primeiros usu", "usuarios"])
        if t:
            resultado["tarefas_concluidas"].append(t)

    if d["leads"] > 0:
        t = _marcar_tarefa_concluida(get_conn, close_conn, ["lead", "contato"])
        if t:
            resultado["tarefas_concluidas"].append(t)

    if d["clientes_pagantes"] > 0:
        t = _marcar_tarefa_concluida(get_conn, close_conn, ["primeiro cliente", "converter primeiro"])
        if t:
            resultado["tarefas_concluidas"].append(t)

    if d["receita_total"] > 0:
        t = _marcar_tarefa_concluida(get_conn, close_conn, ["primeira receita", "receita"])
        if t:
            resultado["tarefas_concluidas"].append(t)

    # ---------- REGRA: SE FASE 2 COMECOU, CRIA TAREFAS PADRAO ----------
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, status FROM roadmap_phases WHERE numero=2 LIMIT 1")
        row = cur.fetchone()
        cur.close()
        close_conn(conn)
        if row and row[1] in ("em_execucao", "concluido", "validado"):
            cur = get_conn().cursor()
            # pega id da meta "5 clientes"
            conn2 = get_conn()
            cur2 = conn2.cursor()
            cur2.execute("SELECT id FROM goals WHERE LOWER(titulo) LIKE '%5 clientes%' LIMIT 1")
            g = cur2.fetchone()
            gid = g[0] if g else None
            cur2.close()
            close_conn(conn2)

            tarefas_padrao = [
                ("Fazer 3 demonstrações do M.A Tech", "critica"),
                ("Conseguir 5 testes ativos", "alta"),
                ("Definir script de abordagem", "alta"),
                ("Criar material de apresentação", "media"),
            ]
            for titulo, prio in tarefas_padrao:
                if _criar_tarefa(get_conn, close_conn, titulo, gid, prio):
                    resultado["tarefas_criadas"].append(titulo)
    except Exception as e:
        resultado["erros"].append(str(e))

    # ---------- REGISTRAR NO DIARIO (apenas se houve mudanca) ----------
    total_mudancas = (len(resultado["tarefas_concluidas"]) +
                      len(resultado["tarefas_criadas"]) +
                      len(resultado["metas_atualizadas"]) +
                      len(resultado["fases_atualizadas"]))
    if total_mudancas > 0:
        resumo = f"Sync: {len(resultado['tarefas_concluidas'])} tarefas concluidas, "
        resumo += f"{len(resultado['tarefas_criadas'])} criadas, "
        resumo += f"{len(resultado['metas_atualizadas'])} metas atualizadas, "
        resumo += f"{len(resultado['fases_atualizadas'])} fases atualizadas."
        _registrar_diario(get_conn, close_conn, "Sync automatico rodou", resumo, "produto", "OK")

    return resultado
