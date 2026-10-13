with open("app.py", "r", encoding="utf-8") as f:
    c = f.read()

antigo = '''def processar_atendimento(aid, linha_crm, mensagem, prompt, hist, whatsapp, uid, cid=None, nicho_dict=None):
    try:
        r = gerar_resposta(linha_crm, mensagem, prompt, hist, nicho_dict=nicho_dict)
        salvar_historico(whatsapp, uid, "ia", r.get("o_que_falar", ""))
        try:
            incrementar_resposta(uid)
        except Exception as _e:
            print("Erro incrementar resposta:", _e)
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE atendimentos SET o_que_falar=%s, texto_para_enviar=%s, acao_crm=%s, linha_crm_gerada=%s, status='pronto' WHERE id=%s", (r.get("o_que_falar", ""), r.get("texto_para_enviar", ""), r.get("estagio", "Em Atendimento"), r.get("linha_crm", ""), aid))
        if cid and r.get("linha_crm"):
            cur.execute("UPDATE clientes SET linha_crm=%s, status=%s, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s", (r["linha_crm"], r["estagio"].lower(), cid))
        conn.commit()
        cur.close()
        close_conn(conn)
    except Exception as e:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE atendimentos SET o_que_falar=%s, status='erro' WHERE id=%s", (f"ERRO: {e}", aid))
        conn.commit()
        cur.close()
        close_conn(conn)'''

novo = '''def processar_atendimento(aid, linha_crm, mensagem, prompt, hist, whatsapp, uid, cid=None, nicho_dict=None):
    try:
        r = gerar_resposta(linha_crm, mensagem, prompt, hist, nicho_dict=nicho_dict)
        salvar_historico(whatsapp, uid, "ia", r.get("o_que_falar", ""))
        try:
            incrementar_resposta(uid)
        except Exception as _e:
            print("Erro incrementar resposta:", _e)
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE atendimentos SET o_que_falar=%s, texto_para_enviar=%s, acao_crm=%s, linha_crm_gerada=%s, status='pronto' WHERE id=%s", (r.get("o_que_falar", ""), r.get("texto_para_enviar", ""), r.get("estagio", "Em Atendimento"), r.get("linha_crm", ""), aid))
        if cid and r.get("linha_crm"):
            cur.execute("UPDATE clientes SET linha_crm=%s, status=%s, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s", (r["linha_crm"], r["estagio"].lower(), cid))
        conn.commit()
        cur.close()
        close_conn(conn)

        # ============================================================
        # IA QUE APRENDE — auditoria automatica
        # ============================================================
        try:
            _rodar_auditoria(aid, uid, r, nicho_dict)
        except Exception as _e:
            print(f"Auditoria erro: {_e}")

    except Exception as e:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE atendimentos SET o_que_falar=%s, status='erro' WHERE id=%s", (f"ERRO: {e}", aid))
        conn.commit()
        cur.close()
        close_conn(conn)


def _rodar_auditoria(aid, uid, r, nicho_dict):
    """Roda auditoria na resposta. So se o cliente tem IA que Aprende ligado."""
    if not nicho_dict:
        return

    # Verifica se o vendedor tem o modo ligado
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT ia_aprende_ativo, analises_acumuladas FROM vendedores WHERE usuario_id = %s", (uid,))
    v = cur.fetchone()
    if not v or not v.get("ia_aprende_ativo"):
        cur.close()
        close_conn(conn)
        return

    # Pega campos extras do nicho
    nicho_id = nicho_dict.get("id")
    campos_extras = {}
    if nicho_id:
        cur.execute("SELECT campo, valor FROM nicho_campos_extras WHERE nicho_id = %s", (nicho_id,))
        for row in cur.fetchall():
            campos_extras[row["campo"]] = row["valor"]

    nicho_dict["campos_extras"] = campos_extras
    cur.close()
    close_conn(conn)

    # Roda o auditor
    import auditor_ia
    analise = auditor_ia.auditar_resposta(r.get("o_que_falar", ""), nicho_dict)

    # Salva a analise no banco
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO analises_ia (atendimento_id, vendedor_id, resposta_analisada, inventou, campo_faltante, o_que_a_ia_disse, pergunta_pro_vendedor)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (aid, uid, r.get("o_que_falar", ""), analise["inventou"], analise["campo"], analise["o_que_a_ia_disse"], analise["pergunta_pro_vendedor"]))

    # Incrementa o contador de analises
    cur.execute("""
        UPDATE vendedores 
        SET analises_acumuladas = COALESCE(analises_acumuladas, 0) + 1
        WHERE usuario_id = %s
        RETURNING analises_acumuladas
    """, (uid,))
    n = cur.fetchone()[0]

    # Se chegou em 3 analises, cobra 1 interacao e zera
    if n >= 3:
        cur.execute("UPDATE vendedores SET analises_acumuladas = 0 WHERE usuario_id = %s", (uid,))
        # Cobra 1 interacao
        try:
            cur.execute("""INSERT INTO respostas_ia (vendedor_id, mes_ano, total)
                           VALUES ((SELECT id FROM vendedores WHERE usuario_id = %s), %s, 1)
                           ON CONFLICT (vendedor_id, mes_ano)
                           DO UPDATE SET total = respostas_ia.total + 1, atualizado_em = CURRENT_TIMESTAMP""",
                        (uid, datetime.now().strftime("%Y-%m")))
            print(f"IA que Aprende: cobrada 1 interacao (3 analises completas) - uid {uid}")
        except Exception as _e:
            print(f"Erro cobrar interacao: {_e}")

    conn.commit()
    cur.close()
    close_conn(conn)
    print(f"IA que Aprende: analise rodada (inventou={analise['inventou']}, campo={analise['campo']}) - {n}/3")'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - auditor integrado no app.py")
else:
    print("ERRO - nao achei o bloco")

# Confirma sintaxe
import subprocess
r = subprocess.run(["python", "-c", "import app; print('OK')"], capture_output=True, text=True)
print(r.stdout)
print(r.stderr[:500] if r.stderr else "")
