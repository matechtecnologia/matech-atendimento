with open("app.py", "r", encoding="utf-8") as f:
    c = f.read()

# Adiciona funcao helper pra verificar se e 1o mes
# Coloca logo depois de "EXCEDENTE_PRECO = ..."
antigo_config = 'EXCEDENTE_PRECO = {"gratis": 0.0, "basico": 0.10, "pro": 0.10, "empresarial": 0.10}'

novo_config = '''EXCEDENTE_PRECO = {"gratis": 0.0, "basico": 0.10, "pro": 0.10, "empresarial": 0.10}


def _e_primeiro_mes(vendedor_id):
    """Verifica se o vendedor nunca foi cobrado."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM primeira_cobranca WHERE vendedor_id = %s", (vendedor_id,))
        r = cur.fetchone()
        cur.close()
        close_conn(conn)
        return r is None
    except Exception as e:
        print(f"erro _e_primeiro_mes: {e}")
        return False


def _preco_para(vendedor_id, plano):
    """Retorna o preco do plano. Se for 1o mes, aplica desconto."""
    if _e_primeiro_mes(vendedor_id):
        return PLANOS_PRECO_1MES.get(plano, PLANOS_PRECO[plano])
    return PLANOS_PRECO[plano]'''

if antigo_config in c:
    c = c.replace(antigo_config, novo_config, 1)
    print("OK - helper _preco_para criada")
else:
    print("ERRO - nao achei bloco de config")

# Troca /assinar
antigo_assinar = '''@app.post("/assinar")
def assinar(request: Request, plano: str = Form(...), valor: str = Form(...), usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None)):
    plano = (plano or "").lower().strip()
    if plano not in PLANOS_PRECO:
        return RedirectResponse(url="/planos", status_code=303)
    valor = f"{PLANOS_PRECO[plano]:.2f}"
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    return templates.TemplateResponse(request=request, name="assinar.html", context={"usuario_nome": usuario_nome, "plano": plano, "valor": valor, "erro": None})'''

novo_assinar = '''@app.post("/assinar")
def assinar(request: Request, plano: str = Form(...), valor: str = Form(...), usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None)):
    plano = (plano or "").lower().strip()
    if plano not in PLANOS_PRECO:
        return RedirectResponse(url="/planos", status_code=303)
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    valor = f"{_preco_para(v['id'], plano):.2f}"
    return templates.TemplateResponse(request=request, name="assinar.html", context={"usuario_nome": usuario_nome, "plano": plano, "valor": valor, "erro": None})'''

if antigo_assinar in c:
    c = c.replace(antigo_assinar, novo_assinar, 1)
    print("OK - /assinar atualizado")
else:
    print("AVISO - /assinar nao achei")

# Troca /gerar_pix
antigo_pix = '''@app.post("/gerar_pix")
def gerar_pix(request: Request, plano: str = Form(...), valor: str = Form(...), cpf_cnpj: str = Form(...), usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None)):
    plano = (plano or "").lower().strip()
    if plano not in PLANOS_PRECO:
        return RedirectResponse(url="/planos", status_code=303)
    valor = f"{PLANOS_PRECO[plano]:.2f}"'''

novo_pix = '''@app.post("/gerar_pix")
def gerar_pix(request: Request, plano: str = Form(...), valor: str = Form(...), cpf_cnpj: str = Form(...), usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None)):
    plano = (plano or "").lower().strip()
    if plano not in PLANOS_PRECO:
        return RedirectResponse(url="/planos", status_code=303)
    v_tmp = buscar_vendedor(usuario_id) if usuario_id else None
    if not v_tmp:
        return RedirectResponse(url="/login")
    valor = f"{_preco_para(v_tmp['id'], plano):.2f}"'''

if antigo_pix in c:
    c = c.replace(antigo_pix, novo_pix, 1)
    print("OK - /gerar_pix atualizado")
else:
    print("AVISO - /gerar_pix nao achei")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - arquivo salvo")
