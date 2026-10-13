with open("app.py", "r", encoding="utf-8") as f:
    c = f.read()

# Adiciona as rotas antes de @app.get("/logout")
rotas = '''

# ============================================================
# IA QUE APRENDE — rotas
# ============================================================

@app.get("/api/ia-aprende/status")
def ia_aprende_status(usuario_id: str = Cookie(None)):
    if not usuario_id:
        return JSONResponse({"ok": False}, status_code=401)
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT ia_aprende_ativo, analises_acumuladas FROM vendedores WHERE usuario_id = %s", (usuario_id,))
        v = cur.fetchone()
        cur.close()
        close_conn(conn)
        if not v:
            return JSONResponse({"ok": False})
        return JSONResponse({
            "ok": True,
            "ativo": bool(v.get("ia_aprende_ativo")),
            "analises_acumuladas": int(v.get("analises_acumuladas") or 0),
        })
    except Exception as e:
        return JSONResponse({"ok": False, "erro": str(e)})


@app.post("/api/ia-aprende/toggle")
async def ia_aprende_toggle(request: Request, usuario_id: str = Cookie(None)):
    if not usuario_id:
        return JSONResponse({"ok": False}, status_code=401)
    try:
        body = await request.json()
        ativo = bool(body.get("ativo", False))
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE vendedores SET ia_aprende_ativo = %s WHERE usuario_id = %s", (ativo, usuario_id))
        conn.commit()
        cur.close()
        close_conn(conn)
        return JSONResponse({"ok": True, "ativo": ativo})
    except Exception as e:
        return JSONResponse({"ok": False, "erro": str(e)})


@app.get("/api/ia-aprende/analise/{atendimento_id}")
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
        return JSONResponse({"ok": False, "erro": str(e)})


@app.post("/api/ia-aprende/corrigir")
async def ia_aprende_corrigir(request: Request, usuario_id: str = Cookie(None)):
    if not usuario_id:
        return JSONResponse({"ok": False}, status_code=401)
    try:
        body = await request.json()
        atendimento_id = int(body.get("atendimento_id", 0))
        campo = (body.get("campo") or "").strip().lower()
        valor = (body.get("valor") or "").strip()
        if not campo or not valor:
            return JSONResponse({"ok": False, "erro": "campo e valor obrigatorios"})

        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Pega o atendimento e o nicho
        cur.execute("SELECT nicho_id FROM atendimentos WHERE id = %s", (atendimento_id,))
        a = cur.fetchone()
        if not a:
            cur.close()
            close_conn(conn)
            return JSONResponse({"ok": False, "erro": "atendimento nao encontrado"})

        nicho_id = a["nicho_id"]

        # Salva o campo extra no nicho
        cur.execute("""
            INSERT INTO nicho_campos_extras (nicho_id, campo, valor)
            VALUES (%s, %s, %s)
            ON CONFLICT (nicho_id, campo)
            DO UPDATE SET valor = EXCLUDED.valor, atualizado_em = NOW()
        """, (nicho_id, campo, valor))

        # Marca a analise como corrigida
        cur.execute("UPDATE analises_ia SET corrigido = TRUE WHERE atendimento_id = %s", (atendimento_id,))

        conn.commit()
        cur.close()
        close_conn(conn)
        return JSONResponse({"ok": True})
    except Exception as e:
        return JSONResponse({"ok": False, "erro": str(e)})

'''

if "/api/ia-aprende/status" not in c:
    c = c.replace('@app.get("/logout")', rotas + '\n\n@app.get("/logout")', 1)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - 4 rotas adicionadas")
else:
    print("AVISO - rotas ja existem")
