import io

path = 'app.py'
with io.open(path, 'r', encoding='utf-8') as f:
    c = f.read()

if 'admin_criar_nicho' in c:
    print("JA TEM as rotas. Nada a fazer.")
else:
    novas_rotas = '''


# ============ ADMIN — CRIAR DADOS PELO VENDEDOR ============

@app.post("/admin/vendedor/{vendedor_id}/nicho/criar")
def admin_criar_nicho(vendedor_id: int, nome: str = Form(...), produto: str = Form(""), publico: str = Form(""), preco: str = Form(""), dor: str = Form(""), objecao: str = Form(""), diferencial: str = Form(""), tom: str = Form(""), usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    pg = gerar_prompt_vendedor(produto, publico, preco, dor, objecao, diferencial, tom)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO nichos (vendedor_id, nome, produto, publico, preco, dor, objecao, diferencial, tom, prompt_gerado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (vendedor_id, nome, produto, publico, preco, dor, objecao, diferencial, tom, pg))
    conn.commit()
    cur.close()
    close_conn(conn)
    return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}?ok=1", status_code=303)


@app.post("/admin/vendedor/{vendedor_id}/cliente/criar")
def admin_criar_cliente(vendedor_id: int, whatsapp: str = Form(...), nome: str = Form(...), email: str = Form(""), origem: str = Form(""), status: str = Form("novo lead"), observacoes: str = Form(""), usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    wpp_limpo, erro_wpp = validar_whatsapp(whatsapp)
    if erro_wpp:
        return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}?erro=WhatsApp+invalido", status_code=303)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM clientes WHERE whatsapp = %s AND vendedor_id = %s", (wpp_limpo, vendedor_id))
    if cur.fetchone():
        cur.close()
        close_conn(conn)
        return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}?erro=Cliente+ja+existe", status_code=303)
    cur.execute("INSERT INTO clientes (vendedor_id, whatsapp, nome, email, origem, status, observacoes) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (vendedor_id, wpp_limpo, nome, email, origem, status, observacoes))
    conn.commit()
    cur.close()
    close_conn(conn)
    return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}?ok=1", status_code=303)


@app.post("/admin/vendedor/{vendedor_id}/editar-whatsapp")
def admin_editar_whatsapp_vendedor(vendedor_id: int, whatsapp: str = Form(...), usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    wpp_limpo, erro_wpp = validar_whatsapp(whatsapp)
    if erro_wpp:
        return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}?erro=WhatsApp+invalido", status_code=303)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT usuario_id FROM vendedores WHERE id = %s", (vendedor_id,))
    row = cur.fetchone()
    if row:
        cur.execute("SELECT id FROM usuarios WHERE whatsapp = %s AND id != %s", (wpp_limpo, row[0]))
        if cur.fetchone():
            cur.close()
            close_conn(conn)
            return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}?erro=WhatsApp+ja+em+uso", status_code=303)
        cur.execute("UPDATE usuarios SET whatsapp = %s WHERE id = %s", (wpp_limpo, row[0]))
        conn.commit()
    cur.close()
    close_conn(conn)
    return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}?ok=1", status_code=303)
'''
    c = c + novas_rotas
    with io.open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print("OK: rotas adicionadas")
    print("Agora reinicia o servidor e testa.")