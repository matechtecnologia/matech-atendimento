import os
import sqlite3
import threading
from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from dotenv import load_dotenv
from gemini import gerar_resposta, gerar_prompt_vendedor

load_dotenv()

app = FastAPI(title="M.A Tech - Atendimento")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# LIMITES POR PLANO

LIMITES = {
    "gratis": 1,
    "basico": 3,
    "pro": 10,
    "empresarial": 999
}

def inicializar_banco():
    conn = sqlite3.connect("dados.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, email TEXT UNIQUE NOT NULL, senha TEXT NOT NULL, tipo TEXT NOT NULL DEFAULT 'atendente', ativo INTEGER NOT NULL DEFAULT 1, criado_em DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS vendedores (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER UNIQUE NOT NULL, plano TEXT DEFAULT 'gratis', onboarding_completo INTEGER DEFAULT 0, criado_em DATETIME DEFAULT CURRENT_TIMESTAMP, atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS nichos (id INTEGER PRIMARY KEY AUTOINCREMENT, vendedor_id INTEGER NOT NULL, nome TEXT NOT NULL, produto TEXT, publico TEXT, preco TEXT, dor TEXT, objecao TEXT, diferencial TEXT, tom TEXT, prompt_gerado TEXT, ativo INTEGER DEFAULT 1, criado_em DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS atendimentos (id INTEGER PRIMARY KEY AUTOINCREMENT, atendente_id INTEGER NOT NULL, nicho_id INTEGER, whatsapp TEXT, linha_crm TEXT, mensagem_cliente TEXT, o_que_falar TEXT, texto_para_enviar TEXT, acao_crm TEXT, linha_crm_gerada TEXT, status TEXT DEFAULT 'processando', criado_em DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS historico (id INTEGER PRIMARY KEY AUTOINCREMENT, whatsapp TEXT NOT NULL, vendedor_id INTEGER NOT NULL, direcao TEXT NOT NULL, mensagem TEXT NOT NULL, criado_em DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, vendedor_id INTEGER NOT NULL, whatsapp TEXT NOT NULL, nome TEXT, email TEXT, origem TEXT, status TEXT DEFAULT 'lead', observacoes TEXT, linha_crm TEXT, nicho_id INTEGER, criado_em DATETIME DEFAULT CURRENT_TIMESTAMP, atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP, UNIQUE(vendedor_id, whatsapp))""")
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

def listar_clientes(vendedor_id):
    conn = sqlite3.connect("dados.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM clientes WHERE vendedor_id = ? ORDER BY atualizado_em DESC", (vendedor_id,))
    clientes = c.fetchall()
    conn.close()
    return clientes

def buscar_cliente_por_whatsapp(whatsapp, vendedor_id):
    conn = sqlite3.connect("dados.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM clientes WHERE whatsapp = ? AND vendedor_id = ?", (whatsapp, vendedor_id))
    cli = c.fetchone()
    conn.close()
    return cli

def salvar_cliente(vendedor_id, whatsapp, nome, email, origem, status, observacoes, linha_crm="", nicho_id=None):
    conn = sqlite3.connect("dados.db")
    c = conn.cursor()
    c.execute("SELECT id FROM clientes WHERE whatsapp = ? AND vendedor_id = ?", (whatsapp, vendedor_id))
    existente = c.fetchone()

    if existente:
        c.execute("""
            UPDATE clientes
            SET nome=?, email=?, origem=?, status=?, observacoes=?, linha_crm=?, nicho_id=?, atualizado_em=CURRENT_TIMESTAMP
            WHERE id=?
        """, (nome, email, origem, status, observacoes, linha_crm, nicho_id, existente[0]))
        cliente_id = existente[0]
    else:
        c.execute("""
            INSERT INTO clientes (vendedor_id, whatsapp, nome, email, origem, status, observacoes, linha_crm, nicho_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (vendedor_id, whatsapp, nome, email, origem, status, observacoes, linha_crm, nicho_id))
        cliente_id = c.lastrowid

    conn.commit()
    conn.close()
    return cliente_id

def atualizar_linha_crm_cliente(cliente_id, nova_linha):
    conn = sqlite3.connect("dados.db")
    c = conn.cursor()
    c.execute("UPDATE clientes SET linha_crm = ?, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?", (nova_linha, cliente_id))
    conn.commit()
    conn.close()

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

        # Atualiza a linha CRM do cliente no banco automaticamente
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
    if not v or not v["onboarding_completo"]:
        destino = "/onboarding"
    else:
        destino = "/atendimento"

    r = RedirectResponse(url=destino, status_code=303)
    r.set_cookie(key="usuario_id", value=str(u["id"]), httponly=True)
    r.set_cookie(key="usuario_nome", value=u["nome"], httponly=True)
    return r

# ========== ONBOARDING (cria o primeiro nicho) ==========
@app.get("/onboarding", response_class=HTMLResponse)
def tela_onboarding(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request=request, name="onboarding.html", context={"usuario_nome": usuario_nome})

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
    return RedirectResponse(url="/atendimento", status_code=303)

# ========== ATENDIMENTO ==========
@app.get("/atendimento", response_class=HTMLResponse)
def tela_atendimento(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v or not v["onboarding_completo"]:
        return RedirectResponse(url="/onboarding")
    nichos = listar_nichos(v["id"])
    return templates.TemplateResponse(request=request, name="atendimento.html", context={"usuario_nome": usuario_nome, "nichos": [dict(n) for n in nichos]})

@app.post("/gerar_resposta")
def rota_gerar_resposta(
    whatsapp: str = Form(...),
    nicho_id: int = Form(...),
    mensagem_cliente: str = Form(...),
    cliente_id: int = Form(None),
    modo_instrucao: str = Form(None),
    usuario_id: str = Cookie(None)
):
    if not usuario_id:
        return RedirectResponse(url="/login")

    if modo_instrucao:
        mensagem_cliente = f"[INSTRUÇÃO DO VENDEDOR — EXECUTE, NÃO RESPONDA COMO CLIENTE]: {mensagem_cliente}"

    nicho = buscar_nicho(nicho_id)
    if not nicho:
        return RedirectResponse(url="/atendimento")
    prompt_vendedor = nicho["prompt_gerado"]

    # Pega a linha CRM do cliente (se existir)
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
def tela_resultado(request: Request, atendimento_id: int, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    conn = sqlite3.connect("dados.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM atendimentos WHERE id = ?", (atendimento_id,))
    a = c.fetchone()
    conn.close()
    if not a:
        return RedirectResponse(url="/atendimento")
    return templates.TemplateResponse(request=request, name="resultado.html", context={"usuario_nome": usuario_nome, "atendimento": dict(a)})

# ========== MEUS NICHOS ==========
@app.get("/meus_nichos", response_class=HTMLResponse)
def tela_meus_nichos(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), erro: str = None):
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
        "nichos": [dict(n) for n in nichos],
        "total": total,
        "limite": limite,
        "plano": v["plano"],
        "erro": erro
    })

@app.get("/novo_nicho", response_class=HTMLResponse)
def tela_novo_nicho(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")

    total = contar_nichos(v["id"])
    limite = LIMITES.get(v["plano"], 1)
    if total >= limite:
        return RedirectResponse(url="/meus_nichos?erro=Limite+atingido.+Faca+upgrade+para+adicionar+mais+nichos.", status_code=303)

    return templates.TemplateResponse(request=request, name="novo_nicho.html", context={"usuario_nome": usuario_nome})

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
def tela_clientes(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None)):
    try:
        if not usuario_id:
            return RedirectResponse(url="/login")
        v = buscar_vendedor(usuario_id)
        if not v:
            return RedirectResponse(url="/onboarding")

        clientes = listar_clientes(v["id"])

        return templates.TemplateResponse(request=request, name="clientes.html", context={
            "usuario_nome": usuario_nome,
            "clientes": [dict(c) for c in clientes]
        })
    except Exception as e:
        import traceback
        erro_completo = traceback.format_exc()
        return HTMLResponse(f"<pre>ERRO: {e}\n\n{erro_completo}</pre>", status_code=500)

@app.post("/salvar_cliente_manual")
def salvar_cliente_manual(
    whatsapp: str = Form(...),
    nome: str = Form(...),
    email: str = Form(""),
    origem: str = Form(""),
    status: str = Form("lead"),
    observacoes: str = Form(""),
    usuario_id: str = Cookie(None)
):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")

    salvar_cliente(v["id"], whatsapp, nome, email, origem, status, observacoes)
    return RedirectResponse(url="/clientes", status_code=303)

@app.post("/salvar_atendimento_como_cliente/{atendimento_id}")
def salvar_atendimento_como_cliente(atendimento_id: int, usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")

    conn = sqlite3.connect("dados.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM atendimentos WHERE id = ?", (atendimento_id,))
    a = c.fetchone()
    conn.close()

    if not a:
        return RedirectResponse(url="/atendimento")

    whatsapp = a["whatsapp"] or ""
    linha_crm = a["linha_crm"] or ""

    # Tenta extrair nome do campo "Nome:" da linha CRM
    nome = ""
    for parte in linha_crm.replace("\n", ";").split(";"):
        if "nome:" in parte.lower():
            nome = parte.split(":", 1)[1].strip()
            break

    salvar_cliente(v["id"], whatsapp, nome, "", "", "lead", linha_crm)
    return RedirectResponse(url="/clientes", status_code=303)

@app.get("/cliente/{cliente_id}/atender", response_class=HTMLResponse)
def atender_cliente(request: Request, cliente_id: int, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None)):
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
        "cliente": dict(cli),
        "nichos": [dict(n) for n in nichos]
    })

@app.get("/cliente/{cliente_id}", response_class=HTMLResponse)
def tela_cliente_detalhe(request: Request, cliente_id: int, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None)):
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
        "cliente": dict(cli),
        "historico": historico
    })


@app.get("/logout")
def logout():
    r = RedirectResponse(url="/login")
    r.delete_cookie("usuario_id")
    r.delete_cookie("usuario_nome")
    return r