with open("app.py", "r", encoding="utf-8") as f:
    c = f.read()

antigo = '''@app.get("/api/ia-aprende/analise/{atendimento_id}")
def ia_aprende_analise(atendimento_id: int, usuario_id: str = Cookie(None)):
    if not usuario_id:
        return JSONResponse({"ok": False}, status_code=401)
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT * FROM analises_ia 
            WHERE atendimento_id = %s AND vendedor_id = %s
            ORDER BY id DESC LIMIT 1
        """, (atendimento_id, usuario_id))
        a = cur.fetchone()
        cur.close()
        close_conn(conn)
        if not a:
            return JSONResponse({"ok": True, "analise": None})
        return JSONResponse({"ok": True, "analise": dict(a)})
    except Exception as e:
        return JSONResponse({"ok": False, "erro": str(e)})'''

novo = '''@app.get("/api/ia-aprende/analise/{atendimento_id}")
def ia_aprende_analise(atendimento_id: int, usuario_id: str = Cookie(None)):
    if not usuario_id:
        return JSONResponse({"ok": False}, status_code=401)
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT * FROM analises_ia 
            WHERE atendimento_id = %s AND vendedor_id = %s
            ORDER BY id DESC LIMIT 1
        """, (atendimento_id, usuario_id))
        a = cur.fetchone()
        
        # Pega o total acumulado
        cur.execute("SELECT analises_acumuladas FROM vendedores WHERE usuario_id = %s", (usuario_id,))
        v = cur.fetchone()
        total = int(v.get("analises_acumuladas") or 0) if v else 0
        
        cur.close()
        close_conn(conn)
        if not a:
            return JSONResponse({"ok": True, "analise": None, "total_analises": total})
        return JSONResponse({"ok": True, "analise": dict(a), "total_analises": total})
    except Exception as e:
        return JSONResponse({"ok": False, "erro": str(e)})'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - rota analise atualizada")
else:
    print("AVISO - rota nao achada")
