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

# ========== INICIALIZAÇÃO AUTOMÁTICA ==========
def inicializar_banco():
    conn = sqlite3.connect("dados.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'atendente',
            ativo INTEGER NOT NULL DEFAULT 1,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS atendimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            atendente_id INTEGER NOT NULL,
            linha_crm TEXT,
            mensagem_cliente TEXT,
            o_que_falar TEXT,
            texto_para_enviar TEXT,
            acao_crm TEXT,
            linha_crm_gerada TEXT,
            status TEXT DEFAULT 'processando',
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER UNIQUE NOT NULL,
            produto TEXT,
            publico TEXT,
            preco TEXT,
            dor TEXT,
            objecao TEXT,
            diferencial TEXT,
            tom TEXT,
            prompt_gerado TEXT,
            onboarding_completo INTEGER DEFAULT 0,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("SELECT * FROM usuarios WHERE email = ?", ("matechtecnologia01@gmail.com",))
    if not cursor.fetchone():
        senha_hash = pwd_context.hash("M@techtechnologia12997291583")
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha, tipo)
            VALUES (?, ?, ?, ?)
        """, ("Admin M.A Tech", "matechtecnologia01@gmail.com", senha_hash, "admin"))

    conn.commit()
    conn.close()
    print("Banco inicializado")

inicializar_banco()
# ========== FIM DA INICIALIZAÇÃO ==========

def buscar_usuario(email):
    conn = sqlite3.connect("dados.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ? AND ativo = 1", (email,))
    usuario = cursor.fetchone()
    conn.close()
    return usuario

def buscar_vendedor(usuario_id):
    conn = sqlite3.connect("dados.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vendedores WHERE usuario_id = ?", (usuario_id,))
    vendedor = cursor.fetchone()
    conn.close()
    return vendedor

def processar_atendimento(atendimento_id, linha_crm, mensagem):
    try:
        resultado = gerar_resposta(linha_crm, mensagem)
        conn = sqlite3.connect("dados.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE atendimentos
            SET o_que_falar = ?, texto_para_enviar = ?, acao_crm = ?, linha_crm_gerada = ?, status = 'pronto'
            WHERE id = ?
        """, (resultado["o_que_falar"], resultado["texto_para_enviar"], resultado["acao_crm"], resultado["linha_crm"], atendimento_id))
        conn.commit()
        conn.close()
    except Exception as e:
        conn = sqlite3.connect("dados.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE atendimentos SET o_que_falar = ?, status = 'erro' WHERE id = ?", (f"ERRO: {e}", atendimento_id))
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
    usuario = buscar_usuario(email)
    if not usuario:
        return RedirectResponse(url="/login?erro=Usuario nao encontrado", status_code=303)
    if not pwd_context.verify(senha, usuario["senha"]):
        return RedirectResponse(url="/login?erro=Senha incorreta", status_code=303)

    vendedor = buscar_vendedor(usuario["id"])
    if not vendedor or not vendedor["onboarding_completo"]:
        destino = "/onboarding"
    else:
        destino = "/atendimento"

    resposta = RedirectResponse(url=destino, status_code=303)
    resposta.set_cookie(key="usuario_id", value=str(usuario["id"]), httponly=True)
    resposta.set_cookie(key="usuario_nome", value=usuario["nome"], httponly=True)
    return resposta

@app.get("/onboarding", response_class=HTMLResponse)
def tela_onboarding(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request=request, name="onboarding.html", context={"usuario_nome": usuario_nome})

@app.post("/salvar_onboarding")
def salvar_onboarding(
    produto: str = Form(...),
    publico: str = Form(...),
    preco: str = Form(...),
    dor: str = Form(...),
    objecao: str = Form(...),
    diferencial: str = Form(...),
    tom: str = Form(...),
    usuario_id: str = Cookie(None)
):
    if not usuario_id:
        return RedirectResponse(url="/login")

    prompt_gerado = gerar_prompt_vendedor(produto, publico, preco, dor, objecao, diferencial, tom)

    conn = sqlite3.connect("dados.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM vendedores WHERE usuario_id = ?", (usuario_id,))
    existente = cursor.fetchone()

    if existente:
        cursor.execute("""
            UPDATE vendedores
            SET produto=?, publico=?, preco=?, dor=?, objecao=?, diferencial=?, tom=?, prompt_gerado=?, onboarding_completo=1, atualizado_em=CURRENT_TIMESTAMP
            WHERE usuario_id=?
        """, (produto, publico, preco, dor, objecao, diferencial, tom, prompt_gerado, usuario_id))
    else:
        cursor.execute("""
            INSERT INTO vendedores (usuario_id, produto, publico, preco, dor, objecao, diferencial, tom, prompt_gerado, onboarding_completo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (usuario_id, produto, publico, preco, dor, objecao, diferencial, tom, prompt_gerado))

    conn.commit()
    conn.close()

    return RedirectResponse(url="/atendimento", status_code=303)

@app.get("/atendimento", response_class=HTMLResponse)
def tela_atendimento(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    vendedor = buscar_vendedor(usuario_id)
    if not vendedor or not vendedor["onboarding_completo"]:
        return RedirectResponse(url="/onboarding")
    return templates.TemplateResponse(request=request, name="atendimento.html", context={"usuario_nome": usuario_nome})

@app.post("/gerar_resposta")
def rota_gerar_resposta(linha_crm: str = Form(...), mensagem_cliente: str = Form(...), usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    conn = sqlite3.connect("dados.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO atendimentos (atendente_id, linha_crm, mensagem_cliente, status) VALUES (?, ?, ?, 'processando')", (usuario_id, linha_crm, mensagem_cliente))
    atendimento_id = cursor.lastrowid
    conn.commit()
    conn.close()
    thread = threading.Thread(target=processar_atendimento, args=(atendimento_id, linha_crm, mensagem_cliente))
    thread.start()
    return RedirectResponse(url=f"/resultado/{atendimento_id}", status_code=303)

@app.get("/resultado/{atendimento_id}", response_class=HTMLResponse)
def tela_resultado(request: Request, atendimento_id: int, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    conn = sqlite3.connect("dados.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM atendimentos WHERE id = ?", (atendimento_id,))
    atendimento = cursor.fetchone()
    conn.close()
    if not atendimento:
        return RedirectResponse(url="/atendimento")
    return templates.TemplateResponse(request=request, name="resultado.html", context={"usuario_nome": usuario_nome, "atendimento": dict(atendimento)})

@app.get("/logout")
def logout():
    resposta = RedirectResponse(url="/login")
    resposta.delete_cookie("usuario_id")
    resposta.delete_cookie("usuario_nome")
    return resposta