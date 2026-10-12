with open("app.py", "r", encoding="utf-8") as f:
    c = f.read()

# Helper pra marcar primeira cobranca
helper = '''

def _marcar_primeira_cobranca(vendedor_id, plano, valor):
    """Registra que o vendedor foi cobrado pela 1a vez (pra aplicar desconto so no 1o mes)."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO primeira_cobranca (vendedor_id, plano, valor_cobrado)
            VALUES (%s, %s, %s)
            ON CONFLICT (vendedor_id) DO NOTHING
        """, (vendedor_id, plano, valor))
        conn.commit()
        cur.close()
        close_conn(conn)
    except Exception as e:
        print(f"Erro _marcar_primeira_cobranca: {e}")

'''

# Adiciona helper antes de @app.get("/pagamento/{payment_id}")
if "def _marcar_primeira_cobranca" not in c:
    c = c.replace(
        '@app.get("/pagamento/{payment_id}", response_class=HTMLResponse)',
        helper + '@app.get("/pagamento/{payment_id}", response_class=HTMLResponse)',
        1
    )
    print("OK - helper adicionado")

# Bloco 1 - tela_pagamento
antigo1 = '''            if row:
                exp = datetime.now() + timedelta(days=30)
                cur.execute("UPDATE vendedores SET plano=%s, plano_expira_em=%s, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s", (p["plano"], exp, row[0]))
                cur.execute("UPDATE pagamentos SET status='pago' WHERE payment_id=%s", (payment_id,))
                conn.commit()
            cur.close()
            close_conn(conn)
            pago = True'''

novo1 = '''            if row:
                exp = datetime.now() + timedelta(days=30)
                cur.execute("UPDATE vendedores SET plano=%s, plano_expira_em=%s, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s", (p["plano"], exp, row[0]))
                cur.execute("UPDATE pagamentos SET status='pago' WHERE payment_id=%s", (payment_id,))
                conn.commit()
                _marcar_primeira_cobranca(row[0], p["plano"], p.get("valor", 0))
            cur.close()
            close_conn(conn)
            pago = True'''

if antigo1 in c:
    c = c.replace(antigo1, novo1, 1)
    print("OK - bloco 1 (tela_pagamento) atualizado")
else:
    print("AVISO - bloco 1 nao achei")

# Bloco 2 - verificar_pagamento
antigo2 = '''        if row:
            exp = datetime.now() + timedelta(days=30)
            cur.execute("UPDATE vendedores SET plano=%s, plano_expira_em=%s, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s", (row[1], exp, row[0]))
            cur.execute("UPDATE pagamentos SET status='pago' WHERE payment_id=%s", (payment_id,))
            conn.commit()
            # Recompensa quem indicou'''

novo2 = '''        if row:
            exp = datetime.now() + timedelta(days=30)
            cur.execute("UPDATE vendedores SET plano=%s, plano_expira_em=%s, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s", (row[1], exp, row[0]))
            cur.execute("UPDATE pagamentos SET status='pago' WHERE payment_id=%s", (payment_id,))
            conn.commit()
            _marcar_primeira_cobranca(row[0], row[1], 0)
            # Recompensa quem indicou'''

if antigo2 in c:
    c = c.replace(antigo2, novo2, 1)
    print("OK - bloco 2 (verificar_pagamento) atualizado")
else:
    print("AVISO - bloco 2 nao achei")

# Bloco 3 - webhook
antigo3 = '''            if row:
                exp = datetime.now() + timedelta(days=30)
                cur.execute("UPDATE vendedores SET plano=%s, plano_expira_em=%s, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s", (row[1], exp, row[0]))
                cur.execute("UPDATE pagamentos SET status='pago' WHERE payment_id=%s", (pid,))
                conn.commit()
            cur.close()
            close_conn(conn)
        return {"status": "ok"}'''

novo3 = '''            if row:
                exp = datetime.now() + timedelta(days=30)
                cur.execute("UPDATE vendedores SET plano=%s, plano_expira_em=%s, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s", (row[1], exp, row[0]))
                cur.execute("UPDATE pagamentos SET status='pago' WHERE payment_id=%s", (pid,))
                conn.commit()
                _marcar_primeira_cobranca(row[0], row[1], 0)
            cur.close()
            close_conn(conn)
        return {"status": "ok"}'''

if antigo3 in c:
    c = c.replace(antigo3, novo3, 1)
    print("OK - bloco 3 (webhook) atualizado")
else:
    print("AVISO - bloco 3 nao achei")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - arquivo salvo")
