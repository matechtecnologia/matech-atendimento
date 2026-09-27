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
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hist_whatsapp ON historico(whatsapp, vendedor_id)")
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

def processar_atendimento(atendimento_id, linha_crm, mensagem, prompt_vendedor, historico, whatsapp, usuario_id):
    try:
        resultado = gerar_resposta(linha_crm, mensagem, prompt_vendedor, historico)
        salvar_historico(whatsapp, usuario_id, "ia", resultado.get("o_que_falar", ""))
        conn = sqlite3.connect("dados.db")
        c = conn.cursor()
        c.execute("""UPDATE atendimentos SET o_que_falar = ?, texto_para_enviar = ?, acao_crm = ?, linha_crm_gerada = ?, status = 'pronto' WHERE id = ?""", (resultado["o_que_falar"], resultado["texto_para_enviar"], resultado["acao_crm"], resultado["linha_crm"], atendimento_id))
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
def rota_gerar_resposta(whatsapp: str = Form(...), nicho_id: int = Form(...), linha_crm: str = Form(...), mensagem_cliente: str = Form(...), modo_instrucao: str = Form(None), usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")

    if modo_instrucao:
        mensagem_cliente = f"[INSTRUÇÃO DO VENDEDOR — EXECUTE, NÃO RESPONDA COMO CLIENTE]: {mensagem_cliente}"

    nicho = buscar_nicho(nicho_id)
    if not nicho:
        return RedirectResponse(url="/atendimento")
    prompt_vendedor = nicho["prompt_gerado"]

    historico = buscar_historico(whatsapp, usuario_id)
    salvar_historico(whatsapp, usuario_id, "cliente", mensagem_cliente)

    conn = sqlite3.connect("dados.db")
    c = conn.cursor()
    c.execute("INSERT INTO atendimentos (atendente_id, nicho_id, whatsapp, linha_crm, mensagem_cliente, status) VALUES (?, ?, ?, ?, ?, 'processando')", (usuario_id, nicho_id, whatsapp, linha_crm, mensagem_cliente))
    atendimento_id = c.lastrowid
    conn.commit()
    conn.close()

    t = threading.Thread(target=processar_atendimento, args=(atendimento_id, linha_crm, mensagem_cliente, prompt_vendedor, historico, whatsapp, usuario_id))
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

@app.get("/logout")
def logout():
    r = RedirectResponse(url="/login")
    r.delete_cookie("usuario_id")
    r.delete_cookie("usuario_nome")
    return r