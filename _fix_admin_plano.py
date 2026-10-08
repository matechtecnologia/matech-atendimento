with open("consultor_rotas.py", "r", encoding="utf-8") as f:
    c = f.read()

antigo = '''def _get_plano(vendedor_id, get_conn, close_conn):
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
        return "gratis"'''

novo = '''def _get_plano(vendedor_id, get_conn, close_conn):
    try:
        conn = get_conn()
        cur = conn.cursor()
        # Admin tem plano ilimitado
        cur.execute("""SELECT u.tipo FROM usuarios u 
                       JOIN vendedores v ON v.usuario_id = u.id 
                       WHERE v.id = %s""", (vendedor_id,))
        r = cur.fetchone()
        if r and r[0] == "admin":
            cur.close()
            close_conn(conn)
            return "admin"
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
        return "gratis"'''

if antigo in c:
    c = c.replace(antigo, novo)
    with open("consultor_rotas.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - admin com limite ilimitado")
else:
    print("ERRO - nao achei o bloco")
