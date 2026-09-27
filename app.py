import os
import sqlite3
import threading
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from dotenv import load_dotenv
from gemini import gerar_resposta, gerar_prompt_vendedor
from asaas import criar_cliente, criar_cobranca_pix, obter_qr_code, consultar_pagamento

load_dotenv()

app = FastAPI(title="M.A Tech - Atendimento")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

LIMITES = {
    "gratis": 1,
    "basico": 3,
    "pro": 10,
    "empresarial": 25
}

def inicializar_banco():
    conn = sqlite3.connect("dados.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, email TEXT UNIQUE NOT NULL, senha TEXT NOT NULL, tipo TEXT NOT NULL DEFAULT 'atendente', ativo INTEGER NOT NULL DEFAULT 1, criado_em DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS vendedores (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER UNIQUE NOT NULL, plano TEXT DEFAULT 'gratis', plano_expira_em DATETIME, onboarding_completo INTEGER DEFAULT 0, criado_em DATETIME DEFAULT CURRENT_TIMESTAMP, atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS nichos (id INTEGER PRIMARY KEY AUTOINCREMENT, vendedor_id INTEGER NOT NULL, nome TEXT NOT NULL, produto TEXT, publico TEXT, preco TEXT, dor TEXT, objecao TEXT, diferencial TEXT, tom TEXT, prompt_gerado TEXT, ativo INTEGER DEFAULT 1, criado_em DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS atendimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, atendente_id INTEGER NOT NULL, nicho_id INTEGER, whatsapp TEXT, linha_crm TEXT, mensagem_cliente TEXT, o_que_falar TEXT, texto_para_enviar TEXT, acao_crm TEXT, linha_crm_gerada TEXT, status TEXT DEFAULT 'processando', criado_em DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS historico (id INTEGER PRIMARY KEY AUTOINCREMENT, whatsapp TEXT NOT NULL, vendedor_id INTEGER NOT NULL, direcao TEXT NOT NULL, mensagem TEXT NOT NULL, criado_em DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, vendedor_id INTEGER NOT NULL, whatsapp TEXT NOT NULL, nome TEXT, email TEXT, origem TEXT, status TEXT DEFAULT 'lead', observacoes TEXT, linha_crm TEXT, nicho_id INTEGER, criado_em DATETIME DEFAULT CURRENT_TIMESTAMP, atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP, UNIQUE(vendedor_id, whatsapp))""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS pagamentos (id INTEGER PRIMARY KEY AUTOINCREMENT, vendedor_id INTEGER, payment_id TEXT, plano TEXT, valor REAL, status TEXT DEFAULT 'pendente', criado_em DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hist_whatsapp ON historico(whatsapp, vendedor_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clientes_vendedor ON clientes(vendedor_id)")
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", ("matechtecnologia01@gmail.com",))
    if not cursor.fetchone():
        senha_hash = pwd_context.hash("M@techtechnologia12997291583")
        cursor.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)", ("Admin M.A Tech", "matechtecnologia01@gmail.com", senha_hash, "admin"))
    conn.commit()
    conn.close()
    print("Banco inicializado")

inicializar_banco()

def buscar_usuario(email):
    conn = sqlite3.connect("dados.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE email = ? AND ativo = 1", (email,))
    u = c.fetchone()
    conn.close()
    return u

def buscar_vendedor(usuario_id):
    conn = sqlite3.connect("dados.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM vendedores WHERE usuario_id = ?", (usuario_id,))
    v = c.fetchone()
    conn.close()
    return v

def listar_nichos(vendedor_id):
    conn = sqlite3.connect("dados.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM nichos WHERE vendedor_id = ? AND ativo = 1 ORDER BY id", (vendedor_id,))
    n = c.fetchall()
    conn.close()
    return n

def contar_nichos(vendedor_id):
    conn = sqlite3.connect("dados.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM nichos WHERE vendedor_id = ? AND ativo = 1", (vendedor_id,))
    total = c.fetchone()[0]
    conn.close()
    return total

def buscar_nicho(nicho_id):
    conn = sqlite3.connect("dados.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM nichos WHERE id = ?", (nicho_id,))
    n = c.fetchone()
    conn.close()
    return n

def verificar_expiracao(vendedor_id):
    conn = sqlite3.connect("dados.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT plano, plano_expira_em FROM vendedores WHERE id = ?", (vendedor_id,))
    v = c.fetchone()
    conn.close()
    if not v or v["plano"] == "gratis" or not v["plano_expira_em"]:
        return
    try:
        expira = datetime.fromisoformat(v["plano_expira_em"])
    except:
        return
    if datetime.now() > expira:
        conn = sqlite3.connect("dados.db")
        c = conn.cursor()
        c.execute("UPDATE vendedores SET plano = 'gratis', plano_expira_em = NULL WHERE id = ?", (vendedor_id,))
        conn.commit()
        conn.close()
        print(f"Plano do vendedor {vendedor_id} expirou.")

def dias_restantes(vendedor_id):
    conn = sqlite3.connect("dados.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT plano_expira_em FROM vendedores WHERE id = ?", (vendedor_id,))
    v = c.fetchone()
    conn.close()
    if not v or not v["plano_expira_em"]:
        return None
    try:
        expira = datetime.fromisoformat(v["plano_expira_em"])
    except:
        return None
    delta = expira - datetime.now()
    return max(0, delta.days)

def criar_vendedor(nome, email, senha):
    conn = sqlite3.connect("dados.db")
    c = conn.cursor()
    c.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
    if c.fetchone():
        conn.close()
        return False, "Email ja cadastrado"
    senha_hash = pwd_context.hash(senha)
    c.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, 'atendente')", (nome, email, senha_hash))
    usuario_id = c.lastrowid
    c.execute("INSERT INTO vendedores (usuario_id, plano, onboarding_completo) VALUES (?, 'gratis', 0)", (usuario_id,))
    conn.commit()
    conn.close()
    return True, "OK"

def listar_todos_vendedores():
    conn = sqlite3.connect("dados.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT u.id, u.nome, u.email, u.criado_em, v.plano, v.id as vendedor_id,
        (SELECT COUNT(*) FROM nichos WHERE vendedor_id = v.id AND ativo=1) as total_nichos,
        (SELECT COUNT(*) FROM clientes WHERE vendedor_id = v.id) as total_clientes
        FROM usuarios u
        LEFT JOIN vendedores v ON v.usuario_id = u.id
        WHERE u.tipo != 'admin' OR u.tipo IS NULL
        ORDER BY u.id DESC
    """)
    vendedores = c.fetchall()
    conn.close()
    return vendedores

def listar_clientes(vendedor_id):
    conn = sqlite3.connect("dados.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM clientes WHERE vendedor_id = ? ORDER BY atualizado_em DESC", (vendedor_id,))
    clientes = c.fetchall()
    conn.close()
    return clientes

def salvar_cliente(vendedor_id, whatsapp, nome, email, origem, status, observacoes, linha_crm="", nicho_id=None):
    conn = sqlite3.connect("dados.db")
    c = conn.cursor()
    c.execute("SELECT id FROM clientes WHERE whatsapp = ? AND vendedor_id = ?", (whatsapp, vendedor_id))
    existente = c.fetchone()
    if existente:
        c.execute("""UPDATE clientes SET nome=?, email=?, origem=?, status=?, observacoes=?, linha_crm=?, nicho_id=?, atualizado_em=CURRENT_TIMESTAMP WHERE id=?""", (nome, email, origem, status, observacoes, linha_crm, nicho_id, existente[0]))
        cliente_id = existente[0]
    else:
        c.execute("""INSERT INTO clientes (vendedor_id, whatsapp, nome, email, origem, status, observacoes, linha_crm, nicho_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (vendedor_id, whatsapp, nome, email, origem, status, observacoes, linha_crm, nicho_id))
        cliente_id = c.lastrowid
    conn.commit()
    conn.close()
    return cliente_id

def buscar_historico(whatsapp, vendedor_id, limite=20):
    conn = sqlite3.connect("dados.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT direcao, mensagem FROM historico WHERE whatsapp = ? AND vendedor_id = ? ORDER BY id DESC LIMIT ?", (whatsapp, vendedor_id, limite))
    linhas = list(reversed(c.fetchall()))
    conn.close()
    if not linhas:
        return ""
    texto = ""
    for l in linhas:
        if l["direcao"] == "cliente":
            texto += f"Cliente: {l['mensagem']}\n"
        else:
            texto += f"Você: {l['mensagem']}\n"
    return texto

def salvar_historico(whatsapp, vendedor_id, direcao, mensagem):
    conn = sqlite3.connect("dados.db")
    c = conn.cursor()
    c.execute("INSERT INTO historico (whatsapp, vendedor_id, direcao, mensagem) VALUES (?, ?, ?, ?)", (whatsapp, vendedor_id, direcao, mensagem))
    c.execute("""DELETE FROM historico WHERE whatsapp = ? AND vendedor_id = ? AND id NOT IN (SELECT id FROM historico WHERE whatsapp = ? AND vendedor_id = ? ORDER BY id DESC LIMIT 20)""", (whatsapp, vendedor_id, whatsapp, vendedor_id))
    conn.commit()
    conn.close()

def processar_atendimento(atendimento_id, linha_crm, mensagem, prompt_vendedor, historico, whatsapp, usuario_id, cliente_id=None):
    try:
        resultado = gerar_resposta(linha_crm, mensagem, prompt_vendedor, historico)
        salvar_historico(whatsapp, usuario_id, "ia", resultado.get("o_que_falar", ""))
        conn = sqlite3.connect("dados.db")
        c = conn.cursor()
        c.execute("""UPDATE atendimentos SET o_que_falar = ?, texto_para_enviar = ?, acao_crm = ?, linha_crm_gerada = ?, status = 'pronto' WHERE id = ?""", (resultado["o_que_falar"], resultado["texto_para_enviar"], resultado["acao_crm"], resultado["linha_crm"], atendimento_id))
        if cliente_id and resultado.get("linha_crm"):
            c.execute("UPDATE clientes SET linha_crm = ?, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?", (resultado["linha_crm"], cliente_id))
        conn.commit()
        conn.close()
    except Exception as e:
        conn = sqlite3.connect("dados.db")
        c = conn.cursor()
        c.execute("UPDATE atendimentos SET o_que_falar = ?, status = 'erro' WHERE id = ?", (f"ERRO: {e}", atendimento_id))
        conn.commit()
        conn.close()

@app.get("/", response_class=HTMLResponse)
def raiz():
    return RedirectResponse(url="/login")

@app.get("/signup", response_class=HTMLResponse)
def tela_signup(request: Request, erro: str = None):
    return templates.TemplateResponse(request=request, name="signup.html", context={"erro": erro})

@app.post("/signup")
def fazer_signup(nome: str = Form(...), email: str = Form(...), senha: str = Form(...)):
    sucesso, msg = criar_vendedor(nome, email, senha)
    if not sucesso:
        return RedirectResponse(url=f"/signup?erro={msg}", status_code=303)
    return RedirectResponse(url="/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
def tela_login(request: Request, erro: str = None):
    return templates.TemplateResponse(request=request, name="login.html", context={"erro": erro})

@app.post("/login")
def fazer_login(email: str = Form(...), senha: str = Form(...)):
    u = buscar_usuario(email)
    if not u:
        return RedirectResponse(url="/login?erro=Usuario nao encontrado", status_code=303)
    if not pwd_context.verify(senha, u["senha"]):
        return RedirectResponse(url="/login?erro=Senha incorreta", status_code=303)

    v = buscar_vendedor(u["id"])
    if v:
        verificar_expiracao(v["id"])

    if u["tipo"] == "admin":
        destino = "/admin"
    else:
        v = buscar_vendedor(u["id"])
        if not v or not v["onboarding_completo"]:
            destino = "/onboarding"
        else:
            destino = "/clientes"

    r = RedirectResponse(url=destino, status_code=303)
    r.set_cookie(key="usuario_id", value=str(u["id"]), httponly=True)
    r.set_cookie(key="usuario_nome", value=u["nome"], httponly=True)
    r.set_cookie(key="usuario_tipo", value=u["tipo"], httponly=True)
    return r

@app.get("/admin", response_class=HTMLResponse)
def tela_admin(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    vendedores = listar_todos_vendedores()
    return templates.TemplateResponse(request=request, name="admin.html", context={
        "usuario_nome": usuario_nome,
        "vendedores": [dict(v) for v in vendedores]
    })

@app.get("/onboarding", response_class=HTMLResponse)
def tela_onboarding(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request=request, name="onboarding.html", context={"usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo})

@app.post("/salvar_onboarding")
def salvar_onboarding(nome_nicho: str = Form(...), produto: str = Form(...), publico: str = Form(...), preco: str = Form(...), dor: str = Form(...), objecao: str = Form(...), diferencial: str = Form(...), tom: str = Form(...), usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    prompt_gerado = gerar_prompt_vendedor(produto, publico, preco, dor, objecao, diferencial, tom)
    conn = sqlite3.connect("dados.db")
    c = conn.cursor()
    c.execute("SELECT id FROM vendedores WHERE usuario_id = ?", (usuario_id,))
    v = c.fetchone()
    if not v:
        c.execute("INSERT INTO vendedores (usuario_id, plano, onboarding_completo) VALUES (?, 'gratis', 1)", (usuario_id,))
        vendedor_id = c.lastrowid
    else:
        vendedor_id = v[0]
        c.execute("UPDATE vendedores SET onboarding_completo = 1, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?", (vendedor_id,))
    c.execute("""INSERT INTO nichos (vendedor_id, nome, produto, publico, preco, dor, objecao, diferencial, tom, prompt_gerado) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (vendedor_id, nome_nicho, produto, publico, preco, dor, objecao, diferencial, tom, prompt_gerado))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/clientes", status_code=303)

@app.get("/atendimento", response_class=HTMLResponse)
def tela_atendimento(request: Request, usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    return RedirectResponse(url="/clientes")

@app.post("/gerar_resposta")
def rota_gerar_resposta(whatsapp: str = Form(...), nicho_id: int = Form(...), mensagem_cliente: str = Form(...), cliente_id: int = Form(None), modo_instrucao: str = Form(None), usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    if modo_instrucao:
        mensagem_cliente = f"[INSTRUÇÃO DO VENDEDOR — EXECUTE, NÃO RESPONDA COMO CLIENTE]: {mensagem_cliente}"
    nicho = buscar_nicho(nicho_id)
    if not nicho:
        return RedirectResponse(url="/clientes")
    prompt_vendedor = nicho["prompt_gerado"]
    linha_crm = ""
    if cliente_id:
        conn = sqlite3.connect("dados.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT linha_crm FROM clientes WHERE id = ?", (cliente_id,))
        cli = c.fetchone()
        conn.close()
        if cli:
            linha_crm = cli["linha_crm"] or ""
    historico = buscar_historico(whatsapp, usuario_id)
    salvar_historico(whatsapp, usuario_id, "cliente", mensagem_cliente)
    conn = sqlite3.connect("dados.db")
    c = conn.cursor()
    c.execute("INSERT INTO atendimentos (atendente_id, nicho_id, whatsapp, linha_crm, mensagem_cliente, status) VALUES (?, ?, ?, ?, ?, 'processando')", (usuario_id, nicho_id, whatsapp, linha_crm, mensagem_cliente))
    atendimento_id = c.lastrowid
    conn.commit()
    conn.close()
    t = threading.Thread(target=processar_atendimento, args=(atendimento_id, linha_crm, mensagem_cliente, prompt_vendedor, historico, whatsapp, usuario_id, cliente_id))
    t.start()
    return RedirectResponse(url=f"/resultado/{atendimento_id}", status_code=303)

@app.get("/resultado/{atendimento_id}", response_class=HTMLResponse)
def tela_resultado(request: Request, atendimento_id: int, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    conn = sqlite3.connect("dados.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM atendimentos WHERE id = ?", (atendimento_id,))
    a = c.fetchone()
    conn.close()
    if not a:
        return RedirectResponse(url="/clientes")
    return templates.TemplateResponse(request=request, name="resultado.html", context={"usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo, "atendimento": dict(a)})

@app.get("/meus_nichos", response_class=HTMLResponse)
def tela_meus_nichos(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None), erro: str = None):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    nichos = listar_nichos(v["id"])
    total = len(nichos)
    limite = LIMITES.get(v["plano"], 1)
    return templates.TemplateResponse(request=request, name="meus_nichos.html", context={
        "usuario_nome": usuario_nome,
        "usuario_tipo": usuario_tipo,
        "nichos": [dict(n) for n in nichos],
        "total": total,
        "limite": limite,
        "plano": v["plano"],
        "erro": erro
    })

@app.get("/novo_nicho", response_class=HTMLResponse)
def tela_novo_nicho(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    total = contar_nichos(v["id"])
    limite = LIMITES.get(v["plano"], 1)
    if total >= limite:
        return RedirectResponse(url="/meus_nichos?erro=Limite+atingido.", status_code=303)
    return templates.TemplateResponse(request=request, name="novo_nicho.html", context={"usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo})

@app.post("/salvar_novo_nicho")
def salvar_novo_nicho(nome_nicho: str = Form(...), produto: str = Form(...), publico: str = Form(...), preco: str = Form(...), dor: str = Form(...), objecao: str = Form(...), diferencial: str = Form(...), tom: str = Form(...), usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    total = contar_nichos(v["id"])
    limite = LIMITES.get(v["plano"], 1)
    if total >= limite:
        return RedirectResponse(url="/meus_nichos?erro=Limite+atingido.", status_code=303)
    prompt_gerado = gerar_prompt_vendedor(produto, publico, preco, dor, objecao, diferencial, tom)
    conn = sqlite3.connect("dados.db")
    c = conn.cursor()
    c.execute("""INSERT INTO nichos (vendedor_id, nome, produto, publico, preco, dor, objecao, diferencial, tom, prompt_gerado) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (v["id"], nome_nicho, produto, publico, preco, dor, objecao, diferencial, tom, prompt_gerado))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/meus_nichos", status_code=303)

@app.get("/clientes", response_class=HTMLResponse)
def tela_clientes(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    clientes = listar_clientes(v["id"])
    return templates.TemplateResponse(request=request, name="clientes.html", context={
        "usuario_nome": usuario_nome,
        "usuario_tipo": usuario_tipo,
        "clientes": [dict(c) for c in clientes]
    })

@app.post("/salvar_cliente_manual")
def salvar_cliente_manual(whatsapp: str = Form(...), nome: str = Form(...), email: str = Form(""), origem: str = Form(""), status: str = Form("lead"), observacoes: str = Form(""), usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    salvar_cliente(v["id"], whatsapp, nome, email, origem, status, observacoes)
    return RedirectResponse(url="/clientes", status_code=303)

@app.get("/cliente/{cliente_id}/atender", response_class=HTMLResponse)
def atender_cliente(request: Request, cliente_id: int, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    conn = sqlite3.connect("dados.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM clientes WHERE id = ? AND vendedor_id = ?", (cliente_id, v["id"]))
    cli = c.fetchone()
    conn.close()
    if not cli:
        return RedirectResponse(url="/clientes")
    nichos = listar_nichos(v["id"])
    return templates.TemplateResponse(request=request, name="atendimento_cliente.html", context={
        "usuario_nome": usuario_nome,
        "usuario_tipo": usuario_tipo,
        "cliente": dict(cli),
        "nichos": [dict(n) for n in nichos]
    })

@app.get("/cliente/{cliente_id}", response_class=HTMLResponse)
def tela_cliente_detalhe(request: Request, cliente_id: int, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    conn = sqlite3.connect("dados.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM clientes WHERE id = ? AND vendedor_id = ?", (cliente_id, v["id"]))
    cli = c.fetchone()
    historico = []
    if cli:
        c.execute("SELECT * FROM historico WHERE whatsapp = ? AND vendedor_id = ? ORDER BY id ASC", (cli["whatsapp"], v["id"]))
        historico = [dict(h) for h in c.fetchall()]
    conn.close()
    if not cli:
        return RedirectResponse(url="/clientes")
    return templates.TemplateResponse(request=request, name="cliente_detalhe.html", context={
        "usuario_nome": usuario_nome,
        "usuario_tipo": usuario_tipo,
        "cliente": dict(cli),
        "historico": historico
    })

@app.get("/planos", response_class=HTMLResponse)
def tela_planos(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    verificar_expiracao(v["id"])
    v = buscar_vendedor(usuario_id)
    dias = dias_restantes(v["id"])
    return templates.TemplateResponse(request=request, name="planos.html", context={
        "usuario_nome": usuario_nome,
        "usuario_tipo": usuario_tipo,
        "plano_atual": v["plano"],
        "dias_restantes": dias
    })

@app.post("/assinar")
def assinar(request: Request, plano: str = Form(...), valor: str = Form(...), usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    return templates.TemplateResponse(request=request, name="assinar.html", context={
        "usuario_nome": usuario_nome,
        "plano": plano,
        "valor": valor,
        "erro": None
    })

@app.post("/gerar_pix")
def gerar_pix(request: Request, plano: str = Form(...), valor: str = Form(...), cpf_cnpj: str = Form(...), usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")

    cpf_cnpj = "".join(filter(str.isdigit, cpf_cnpj))
    if len(cpf_cnpj) not in [11, 14]:
        return templates.TemplateResponse(request=request, name="assinar.html", context={
            "usuario_nome": usuario_nome, "plano": plano, "valor": valor,
            "erro": "CPF/CNPJ invalido. Deve ter 11 ou 14 digitos."
        })

    conn = sqlite3.connect("dados.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
    u = c.fetchone()
    conn.close()

    customer_id = criar_cliente(u["nome"], u["email"], cpf_cnpj)
    if not customer_id:
        return templates.TemplateResponse(request=request, name="assinar.html", context={
            "usuario_nome": usuario_nome, "plano": plano, "valor": valor,
            "erro": "Erro ao criar cliente no Asaas. Verifique o CPF."
        })

    vencimento = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    descricao = f"M.A Tech - Plano {plano.upper()}"

    payment_id = criar_cobranca_pix(customer_id, float(valor), descricao, vencimento)
    if not payment_id:
        return templates.TemplateResponse(request=request, name="assinar.html", context={
            "usuario_nome": usuario_nome, "plano": plano, "valor": valor,
            "erro": "Erro ao criar cobranca. Tente novamente."
        })

    conn = sqlite3.connect("dados.db")
    c = conn.cursor()
    c.execute("INSERT INTO pagamentos (vendedor_id, payment_id, plano, valor) VALUES (?, ?, ?, ?)",
              (v["id"], payment_id, plano, float(valor)))
    conn.commit()
    conn.close()

    return RedirectResponse(url=f"/pagamento/{payment_id}", status_code=303)

@app.get("/pagamento/{payment_id}", response_class=HTMLResponse)
def tela_pagamento(request: Request, payment_id: str, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")

    conn = sqlite3.connect("dados.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT plano, valor, status FROM pagamentos WHERE payment_id = ?", (payment_id,))
    p = c.fetchone()
    conn.close()

    qr = obter_qr_code(payment_id)
    pago = p and p["status"] == "pago"

    return templates.TemplateResponse(request=request, name="pagamento_pix.html", context={
        "usuario_nome": usuario_nome,
        "qr_code": qr,
        "plano": p["plano"] if p else "—",
        "valor": f"{p['valor']:.2f}".replace(".", ",") if p else "0,00",
        "payment_id": payment_id,
        "pago": pago
    })

@app.get("/verificar_pagamento/{payment_id}")
def verificar_pagamento(payment_id: str, usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")

    # Consulta o status direto no Asaas
    info = consultar_pagamento(payment_id)
    status_asaas = info.get("status") if info else None

    if status_asaas in ["CONFIRMED", "RECEIVED"]:
        # Faz o upgrade
        conn = sqlite3.connect("dados.db")
        c = conn.cursor()
        c.execute("SELECT vendedor_id, plano FROM pagamentos WHERE payment_id = ?", (payment_id,))
        row = c.fetchone()
        if row:
            vendedor_id = row[0]
            plano = row[1]
            expira_em = (datetime.now() + timedelta(days=30)).isoformat()
            c.execute("UPDATE vendedores SET plano = ?, plano_expira_em = ?, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?", (plano, expira_em, vendedor_id))
            c.execute("UPDATE pagamentos SET status = 'pago' WHERE payment_id = ?", (payment_id,))
            conn.commit()
        conn.close()

    return RedirectResponse(url=f"/pagamento/{payment_id}", status_code=303)

@app.post("/webhook/asaas")
async def webhook_asaas(request: Request):
    try:
        body = await request.json()
        evento = body.get("event", "")
        payment = body.get("payment", {})
        payment_id = payment.get("id", "")
        print(f"Webhook Asaas: {evento} - {payment_id}")
        if evento in ["PAYMENT_CONFIRMED", "PAYMENT_RECEIVED"]:
            conn = sqlite3.connect("dados.db")
            c = conn.cursor()
            c.execute("SELECT vendedor_id, plano FROM pagamentos WHERE payment_id = ?", (payment_id,))
            row = c.fetchone()
            if row:
                vendedor_id = row[0]
                plano = row[1]
                expira_em = (datetime.now() + timedelta(days=30)).isoformat()
                c.execute("UPDATE vendedores SET plano = ?, plano_expira_em = ?, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?", (plano, expira_em, vendedor_id))
                c.execute("UPDATE pagamentos SET status = 'pago' WHERE payment_id = ?", (payment_id,))
                conn.commit()
                print(f"Plano {plano} ativado para vendedor {vendedor_id}")
            conn.close()
        return {"status": "ok"}
    except Exception as e:
        print(f"Erro webhook: {e}")
        return {"status": "erro"}

@app.get("/logout")
def logout():
    r = RedirectResponse(url="/login")
    r.delete_cookie("usuario_id")
    r.delete_cookie("usuario_nome")
    r.delete_cookie("usuario_tipo")
    return r