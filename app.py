import os
import threading
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from dotenv import load_dotenv
from gemini import gerar_resposta, gerar_prompt_vendedor
from asaas import criar_cliente, criar_cobranca_pix, obter_qr_code, consultar_pagamento

load_dotenv()

app = FastAPI(title="M.A Tech")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

LIMITES = {"gratis": 1, "basico": 3, "pro": 10, "empresarial": 25}
from psycopg2 import pool as pg_pool

DATABASE_URL = os.getenv("DATABASE_URL")

_pool = None

def get_conn():
    global _pool
    if _pool is None:
        _pool = pg_pool.ThreadedConnectionPool(1, 20, dsn=DATABASE_URL, sslmode='require')
    return _pool.getconn()

def close_conn(conn):
    global _pool
    if conn is None:
        return
    try:
        if _pool:
            _pool.putconn(conn)
        else:
            conn.close()
    except Exception:
        try:
            conn.close()
        except Exception:
            pass


def inicializar_banco():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        tipo TEXT NOT NULL DEFAULT 'atendente',
        ativo BOOLEAN NOT NULL DEFAULT TRUE,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS vendedores (
        id SERIAL PRIMARY KEY,
        usuario_id INTEGER UNIQUE NOT NULL,
        plano TEXT DEFAULT 'gratis',
        plano_expira_em TIMESTAMP WITH TIME ZONE,
        onboarding_completo BOOLEAN DEFAULT FALSE,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS nichos (
        id SERIAL PRIMARY KEY,
        vendedor_id INTEGER NOT NULL,
        nome TEXT NOT NULL,
        produto TEXT,
        publico TEXT,
        preco TEXT,
        dor TEXT,
        objecao TEXT,
        diferencial TEXT,
        tom TEXT,
        prompt_gerado TEXT,
        ativo BOOLEAN DEFAULT TRUE,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS atendimentos (
        id SERIAL PRIMARY KEY,
        atendente_id INTEGER NOT NULL,
        nicho_id INTEGER,
        whatsapp TEXT,
        linha_crm TEXT,
        mensagem_cliente TEXT,
        o_que_falar TEXT,
        texto_para_enviar TEXT,
        acao_crm TEXT,
        linha_crm_gerada TEXT,
        cliente_id INTEGER,
        status TEXT DEFAULT 'processando',
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS historico (
        id SERIAL PRIMARY KEY,
        whatsapp TEXT NOT NULL,
        vendedor_id INTEGER NOT NULL,
        direcao TEXT NOT NULL,
        mensagem TEXT NOT NULL,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS clientes (
        id SERIAL PRIMARY KEY,
        vendedor_id INTEGER NOT NULL,
        whatsapp TEXT NOT NULL,
        nome TEXT,
        email TEXT,
        origem TEXT,
        status TEXT DEFAULT 'novo lead',
        observacoes TEXT,
        linha_crm TEXT,
        nicho_id INTEGER,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(vendedor_id, whatsapp)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS pagamentos (
        id SERIAL PRIMARY KEY,
        vendedor_id INTEGER,
        payment_id TEXT,
        plano TEXT,
        valor REAL,
        status TEXT DEFAULT 'pendente',
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("CREATE INDEX IF NOT EXISTS idx_hist_whatsapp ON historico(whatsapp, vendedor_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_clientes_vendedor ON clientes(vendedor_id)")

    cur.execute("SELECT * FROM usuarios WHERE email = %s", ("matechtecnologia01@gmail.com",))
    if not cur.fetchone():
        h = pwd_context.hash("M@techtechnologia12997291583")
        cur.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES (%s, %s, %s, 'admin')", ("Admin M.A Tech", "matechtecnologia01@gmail.com", h))

    conn.commit()
    cur.close()
    close_conn(conn)
    print("Banco inicializado")


try:
    inicializar_banco()
except Exception as e:
    print(f"Erro ao inicializar banco: {e}")


@app.get("/", response_class=HTMLResponse)
def raiz(request: Request, usuario_id: str = Cookie(None)):
    if usuario_id:
        return RedirectResponse(url="/clientes")
    return templates.TemplateResponse(request=request, name="landing.html", context={})

def buscar_usuario(email):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM usuarios WHERE email = %s AND ativo = TRUE", (email,))
    u = cur.fetchone()
    cur.close()
    close_conn(conn)
    return u


def buscar_vendedor(uid):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM vendedores WHERE usuario_id = %s", (uid,))
    v = cur.fetchone()
    cur.close()
    close_conn(conn)
    return v


def listar_nichos(vid):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM nichos WHERE vendedor_id = %s AND ativo = TRUE ORDER BY id", (vid,))
    n = cur.fetchall()
    cur.close()
    close_conn(conn)
    return n


def contar_nichos(vid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM nichos WHERE vendedor_id = %s AND ativo = TRUE", (vid,))
    t = cur.fetchone()[0]
    cur.close()
    close_conn(conn)
    return t


def buscar_nicho(nid):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM nichos WHERE id = %s", (nid,))
    n = cur.fetchone()
    cur.close()
    close_conn(conn)
    return n


def verificar_expiracao(vid):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT plano, plano_expira_em FROM vendedores WHERE id = %s", (vid,))
    v = cur.fetchone()
    cur.close()
    close_conn(conn)
    if not v or v["plano"] == "gratis" or not v["plano_expira_em"]:
        return
    if datetime.now(v["plano_expira_em"].tzinfo) > v["plano_expira_em"]:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE vendedores SET plano = 'gratis', plano_expira_em = NULL WHERE id = %s", (vid,))
        conn.commit()
        cur.close()
        close_conn(conn)


def dias_restantes(vid):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT plano_expira_em FROM vendedores WHERE id = %s", (vid,))
    v = cur.fetchone()
    cur.close()
    close_conn(conn)
    if not v or not v["plano_expira_em"]:
        return None
    delta = v["plano_expira_em"] - datetime.now(v["plano_expira_em"].tzinfo)
    return max(0, delta.days)


def criar_vendedor(nome, email, senha):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
    if cur.fetchone():
        cur.close()
        close_conn(conn)
        return False, "Email ja cadastrado"
    h = pwd_context.hash(senha)
    cur.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES (%s, %s, %s, 'atendente') RETURNING id", (nome, email, h))
    uid = cur.fetchone()[0]
    cur.execute("INSERT INTO vendedores (usuario_id, plano, onboarding_completo) VALUES (%s, 'gratis', FALSE)", (uid,))
    conn.commit()
    cur.close()
    close_conn(conn)
    return True, "OK"


def listar_todos_vendedores():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT u.id, u.nome, u.email, u.criado_em, v.plano, v.id as vendedor_id,
        (SELECT COUNT(*) FROM nichos WHERE vendedor_id = v.id AND ativo=TRUE) as total_nichos,
        (SELECT COUNT(*) FROM clientes WHERE vendedor_id = v.id) as total_clientes
        FROM usuarios u LEFT JOIN vendedores v ON v.usuario_id = u.id
        WHERE u.tipo != 'admin' OR u.tipo IS NULL ORDER BY u.id DESC
    """)
    v = cur.fetchall()
    cur.close()
    close_conn(conn)
    return v


def listar_clientes(vid):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM clientes WHERE vendedor_id = %s ORDER BY atualizado_em DESC", (vid,))
    cli = cur.fetchall()
    cur.close()
    close_conn(conn)
    return cli


def salvar_cliente(vid, whatsapp, nome, email, origem, status, obs, linha_crm="", nicho_id=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM clientes WHERE whatsapp = %s AND vendedor_id = %s", (whatsapp, vid))
    ex = cur.fetchone()
    if ex:
        cur.execute("UPDATE clientes SET nome=%s, email=%s, origem=%s, status=%s, observacoes=%s, linha_crm=%s, nicho_id=%s, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s", (nome, email, origem, status, obs, linha_crm, nicho_id, ex[0]))
        cid = ex[0]
    else:
        cur.execute("INSERT INTO clientes (vendedor_id, whatsapp, nome, email, origem, status, observacoes, linha_crm, nicho_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id", (vid, whatsapp, nome, email, origem, status, obs, linha_crm, nicho_id))
        cid = cur.fetchone()[0]
    conn.commit()
    cur.close()
    close_conn(conn)
    return cid


def buscar_historico(whatsapp, vid, limite=20):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT direcao, mensagem FROM historico WHERE whatsapp = %s AND vendedor_id = %s ORDER BY id DESC LIMIT %s", (whatsapp, vid, limite))
    linhas = list(reversed(cur.fetchall()))
    cur.close()
    close_conn(conn)
    if not linhas:
        return ""
    t = ""
    for l in linhas:
        prefixo = "Cliente" if l["direcao"] == "cliente" else "Voce"
        t += f"{prefixo}: {l['mensagem']}\n"
    return t


def salvar_historico(whatsapp, vid, direcao, mensagem):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO historico (whatsapp, vendedor_id, direcao, mensagem) VALUES (%s, %s, %s, %s)", (whatsapp, vid, direcao, mensagem))
    cur.execute("""DELETE FROM historico WHERE whatsapp = %s AND vendedor_id = %s AND id NOT IN (SELECT id FROM historico WHERE whatsapp = %s AND vendedor_id = %s ORDER BY id DESC LIMIT 20)""", (whatsapp, vid, whatsapp, vid))
    conn.commit()
    cur.close()
    close_conn(conn)


def processar_atendimento(aid, linha_crm, mensagem, prompt, hist, whatsapp, uid, cid=None):
    try:
        r = gerar_resposta(linha_crm, mensagem, prompt, hist)
        salvar_historico(whatsapp, uid, "ia", r.get("o_que_falar", ""))
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE atendimentos SET o_que_falar=%s, texto_para_enviar=%s, acao_crm=%s, linha_crm_gerada=%s, status='pronto' WHERE id=%s", (r["o_que_falar"], r["texto_para_enviar"], r["estagio"], r["linha_crm"], aid))
        if cid and r.get("linha_crm"):
            cur.execute("UPDATE clientes SET linha_crm=%s, status=%s, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s", (r["linha_crm"], r["estagio"].lower(), cid))
        conn.commit()
        cur.close()
        close_conn(conn)
    except Exception as e:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE atendimentos SET o_que_falar=%s, status='erro' WHERE id=%s", (f"ERRO: {e}", aid))
        conn.commit()
        cur.close()
        close_conn(conn)


# ============ ROTAS ============

@app.get("/", response_class=HTMLResponse)
def raiz():
    return RedirectResponse(url="/login")


@app.get("/signup", response_class=HTMLResponse)
def tela_signup(request: Request, erro: str = None):
    return templates.TemplateResponse(request=request, name="signup.html", context={"erro": erro})


@app.post("/signup")
def fazer_signup(nome: str = Form(...), email: str = Form(...), senha: str = Form(...)):
    ok, msg = criar_vendedor(nome, email, senha)
    if not ok:
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
        destino = "/onboarding" if (not v or not v["onboarding_completo"]) else "/clientes"
    r = RedirectResponse(url=destino, status_code=303)
    r.set_cookie(key="usuario_id", value=str(u["id"]), httponly=True)
    r.set_cookie(key="usuario_nome", value=u["nome"], httponly=True)
    r.set_cookie(key="usuario_tipo", value=u["tipo"], httponly=True)
    return r


@app.get("/admin", response_class=HTMLResponse)
def tela_admin(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    vs = listar_todos_vendedores()
    return templates.TemplateResponse(request=request, name="admin.html", context={"usuario_nome": usuario_nome, "vendedores": [dict(v) for v in vs]})


@app.get("/onboarding", response_class=HTMLResponse)
def tela_onboarding(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request=request, name="onboarding.html", context={"usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo})


@app.post("/salvar_onboarding")
def salvar_onboarding(nome_nicho: str = Form(...), produto: str = Form(...), publico: str = Form(...), preco: str = Form(...), dor: str = Form(...), objecao: str = Form(...), diferencial: str = Form(...), tom: str = Form(...), usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    pg = gerar_prompt_vendedor(produto, publico, preco, dor, objecao, diferencial, tom)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM vendedores WHERE usuario_id = %s", (usuario_id,))
    v = cur.fetchone()
    if not v:
        cur.execute("INSERT INTO vendedores (usuario_id, plano, onboarding_completo) VALUES (%s, 'gratis', TRUE) RETURNING id", (usuario_id,))
        vid = cur.fetchone()[0]
    else:
        vid = v[0]
        cur.execute("UPDATE vendedores SET onboarding_completo=TRUE, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s", (vid,))
    cur.execute("INSERT INTO nichos (vendedor_id, nome, produto, publico, preco, dor, objecao, diferencial, tom, prompt_gerado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (vid, nome_nicho, produto, publico, preco, dor, objecao, diferencial, tom, pg))
    conn.commit()
    cur.close()
    close_conn(conn)
    return RedirectResponse(url="/clientes", status_code=303)


@app.get("/clientes", response_class=HTMLResponse)
def tela_clientes(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    cli = listar_clientes(v["id"])
    return templates.TemplateResponse(request=request, name="clientes.html", context={"usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo, "clientes": [dict(c) for c in cli]})


@app.post("/salvar_cliente_manual")
def salvar_cliente_manual(whatsapp: str = Form(...), nome: str = Form(...), email: str = Form(""), origem: str = Form(""), status: str = Form("novo lead"), observacoes: str = Form(""), usuario_id: str = Cookie(None)):
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
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM clientes WHERE id = %s AND vendedor_id = %s", (cliente_id, v["id"]))
    cli = cur.fetchone()
    cur.close()
    close_conn(conn)
    if not cli:
        return RedirectResponse(url="/clientes")
    ns = listar_nichos(v["id"])
    return templates.TemplateResponse(request=request, name="atendimento_cliente.html", context={"usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo, "cliente": dict(cli), "nichos": [dict(n) for n in ns]})


@app.get("/cliente/{cliente_id}", response_class=HTMLResponse)
def tela_cliente_detalhe(request: Request, cliente_id: int, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM clientes WHERE id = %s AND vendedor_id = %s", (cliente_id, v["id"]))
    cli = cur.fetchone()
    hist = []
    if cli:
        cur.execute("SELECT * FROM historico WHERE whatsapp = %s AND vendedor_id = %s ORDER BY id ASC", (cli["whatsapp"], v["id"]))
        hist = [dict(h) for h in cur.fetchall()]
    cur.close()
    close_conn(conn)
    if not cli:
        return RedirectResponse(url="/clientes")
    return templates.TemplateResponse(request=request, name="cliente_detalhe.html", context={"usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo, "cliente": dict(cli), "historico": hist})


@app.post("/gerar_resposta")
def rota_gerar_resposta(whatsapp: str = Form(...), nicho_id: int = Form(...), mensagem_cliente: str = Form(...), cliente_id: int = Form(None), modo_instrucao: str = Form(None), usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    if modo_instrucao:
        mensagem_cliente = f"[INSTRUCAO DO VENDEDOR - EXECUTE]: {mensagem_cliente}"
    n = buscar_nicho(nicho_id)
    if not n:
        return RedirectResponse(url="/clientes")
    linha_crm = ""
    if cliente_id:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT linha_crm FROM clientes WHERE id = %s", (cliente_id,))
        cli = cur.fetchone()
        cur.close()
        close_conn(conn)
        if cli:
            linha_crm = cli["linha_crm"] or ""
    hist = buscar_historico(whatsapp, usuario_id)
    salvar_historico(whatsapp, usuario_id, "cliente", mensagem_cliente)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO atendimentos (atendente_id, nicho_id, whatsapp, linha_crm, mensagem_cliente, cliente_id, status) VALUES (%s, %s, %s, %s, %s, %s, 'processando') RETURNING id", (usuario_id, nicho_id, whatsapp, linha_crm, mensagem_cliente, cliente_id))
    aid = cur.fetchone()[0]
    conn.commit()
    cur.close()
    close_conn(conn)
    threading.Thread(target=processar_atendimento, args=(aid, linha_crm, mensagem_cliente, n["prompt_gerado"], hist, whatsapp, usuario_id, cliente_id)).start()
    return RedirectResponse(url=f"/resultado/{aid}", status_code=303)


@app.get("/resultado/{atendimento_id}", response_class=HTMLResponse)
def tela_resultado(request: Request, atendimento_id: int, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM atendimentos WHERE id = %s", (atendimento_id,))
    a = cur.fetchone()
    cur.close()
    close_conn(conn)
    if not a:
        return RedirectResponse(url="/clientes")
    return templates.TemplateResponse(request=request, name="resultado.html", context={"usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo, "atendimento": dict(a)})


@app.post("/salvar_atendimento_como_cliente/{atendimento_id}")
def salvar_atendimento_como_cliente(atendimento_id: int, usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM atendimentos WHERE id = %s", (atendimento_id,))
    a = cur.fetchone()
    cur.close()
    close_conn(conn)
    if not a:
        return RedirectResponse(url="/clientes")
    whatsapp = a["whatsapp"] or ""
    linha_crm = a["linha_crm"] or ""
    nome = ""
    for parte in linha_crm.replace("\n", ";").split(";"):
        if "nome:" in parte.lower():
            nome = parte.split(":", 1)[1].strip()
            break
    cid = salvar_cliente(v["id"], whatsapp, nome, "", "", "novo lead", linha_crm)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE atendimentos SET cliente_id = %s WHERE id = %s", (cid, atendimento_id))
    conn.commit()
    cur.close()
    close_conn(conn)
    return RedirectResponse(url="/clientes", status_code=303)


@app.get("/meus_nichos", response_class=HTMLResponse)
def tela_meus_nichos(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None), erro: str = None):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    ns = listar_nichos(v["id"])
    return templates.TemplateResponse(request=request, name="meus_nichos.html", context={"usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo, "nichos": [dict(n) for n in ns], "total": len(ns), "limite": LIMITES.get(v["plano"], 1), "plano": v["plano"], "erro": erro})


@app.get("/novo_nicho", response_class=HTMLResponse)
def tela_novo_nicho(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    if contar_nichos(v["id"]) >= LIMITES.get(v["plano"], 1):
        return RedirectResponse(url="/meus_nichos?erro=Limite+atingido", status_code=303)
    return templates.TemplateResponse(request=request, name="novo_nicho.html", context={"usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo})


@app.post("/salvar_novo_nicho")
def salvar_novo_nicho(nome_nicho: str = Form(...), produto: str = Form(...), publico: str = Form(...), preco: str = Form(...), dor: str = Form(...), objecao: str = Form(...), diferencial: str = Form(...), tom: str = Form(...), usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    if contar_nichos(v["id"]) >= LIMITES.get(v["plano"], 1):
        return RedirectResponse(url="/meus_nichos?erro=Limite+atingido", status_code=303)
    pg = gerar_prompt_vendedor(produto, publico, preco, dor, objecao, diferencial, tom)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO nichos (vendedor_id, nome, produto, publico, preco, dor, objecao, diferencial, tom, prompt_gerado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (v["id"], nome_nicho, produto, publico, preco, dor, objecao, diferencial, tom, pg))
    conn.commit()
    cur.close()
    close_conn(conn)
    return RedirectResponse(url="/meus_nichos", status_code=303)


@app.get("/planos", response_class=HTMLResponse)
def tela_planos(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    verificar_expiracao(v["id"])
    v = buscar_vendedor(usuario_id)
    d = dias_restantes(v["id"])
    return templates.TemplateResponse(request=request, name="planos.html", context={"usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo, "plano_atual": v["plano"], "dias_restantes": d})


@app.post("/assinar")
def assinar(request: Request, plano: str = Form(...), valor: str = Form(...), usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    return templates.TemplateResponse(request=request, name="assinar.html", context={"usuario_nome": usuario_nome, "plano": plano, "valor": valor, "erro": None})


@app.post("/gerar_pix")
def gerar_pix(request: Request, plano: str = Form(...), valor: str = Form(...), cpf_cnpj: str = Form(...), usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    cpf_limpo = "".join(filter(str.isdigit, cpf_cnpj))
    if len(cpf_limpo) not in [11, 14]:
        return templates.TemplateResponse(request=request, name="assinar.html", context={"usuario_nome": usuario_nome, "plano": plano, "valor": valor, "erro": f"CPF invalido: {len(cpf_limpo)} digitos"})
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM usuarios WHERE id = %s", (usuario_id,))
    u = cur.fetchone()
    cur.close()
    close_conn(conn)
    customer_id = criar_cliente(u["nome"], u["email"], cpf_limpo)
    if not customer_id:
        return templates.TemplateResponse(request=request, name="assinar.html", context={"usuario_nome": usuario_nome, "plano": plano, "valor": valor, "erro": f"Erro Asaas. CPF: {cpf_limpo}."})
    venc = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    pid = criar_cobranca_pix(customer_id, float(valor), f"M.A Tech - {plano.upper()}", venc)
    if not pid:
        return templates.TemplateResponse(request=request, name="assinar.html", context={"usuario_nome": usuario_nome, "plano": plano, "valor": valor, "erro": "Erro ao criar cobranca PIX."})
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO pagamentos (vendedor_id, payment_id, plano, valor) VALUES (%s, %s, %s, %s)", (v["id"], pid, plano, float(valor)))
    conn.commit()
    cur.close()
    close_conn(conn)
    return RedirectResponse(url=f"/pagamento/{pid}", status_code=303)


@app.get("/pagamento/{payment_id}", response_class=HTMLResponse)
def tela_pagamento(request: Request, payment_id: str, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT plano, valor, status FROM pagamentos WHERE payment_id = %s", (payment_id,))
    p = cur.fetchone()
    cur.close()
    close_conn(conn)
    if not p:
        return RedirectResponse(url="/planos")
    pago = p["status"] == "pago"
    if not pago:
        info = consultar_pagamento(payment_id)
        st = info.get("status") if info else None
        if st in ["CONFIRMED", "RECEIVED"]:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT vendedor_id FROM pagamentos WHERE payment_id = %s", (payment_id,))
            row = cur.fetchone()
            if row:
                exp = datetime.now() + timedelta(days=30)
                cur.execute("UPDATE vendedores SET plano=%s, plano_expira_em=%s, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s", (p["plano"], exp, row[0]))
                cur.execute("UPDATE pagamentos SET status='pago' WHERE payment_id=%s", (payment_id,))
                conn.commit()
            cur.close()
            close_conn(conn)
            pago = True
    qr = None
    if not pago:
        qr = obter_qr_code(payment_id)
    return templates.TemplateResponse(request=request, name="pagamento_pix.html", context={"usuario_nome": usuario_nome, "qr_code": qr, "plano": p["plano"], "valor": f"{p['valor']:.2f}".replace(".", ","), "payment_id": payment_id, "pago": pago})


@app.get("/verificar_pagamento/{payment_id}")
def verificar_pagamento(payment_id: str, usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    info = consultar_pagamento(payment_id)
    st = info.get("status") if info else None
    if st in ["CONFIRMED", "RECEIVED"]:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT vendedor_id, plano FROM pagamentos WHERE payment_id = %s", (payment_id,))
        row = cur.fetchone()
        if row:
            exp = datetime.now() + timedelta(days=30)
            cur.execute("UPDATE vendedores SET plano=%s, plano_expira_em=%s, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s", (row[1], exp, row[0]))
            cur.execute("UPDATE pagamentos SET status='pago' WHERE payment_id=%s", (payment_id,))
            conn.commit()
        cur.close()
        close_conn(conn)
    return RedirectResponse(url=f"/pagamento/{payment_id}", status_code=303)


@app.post("/webhook/asaas")
async def webhook_asaas(request: Request):
    try:
        body = await request.json()
        ev = body.get("event", "")
        pay = body.get("payment", {})
        pid = pay.get("id", "")
        print(f"Webhook: {ev} - {pid}")
        if ev in ["PAYMENT_CONFIRMED", "PAYMENT_RECEIVED"]:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT vendedor_id, plano FROM pagamentos WHERE payment_id = %s", (pid,))
            row = cur.fetchone()
            if row:
                exp = datetime.now() + timedelta(days=30)
                cur.execute("UPDATE vendedores SET plano=%s, plano_expira_em=%s, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s", (row[1], exp, row[0]))
                cur.execute("UPDATE pagamentos SET status='pago' WHERE payment_id=%s", (pid,))
                conn.commit()
            cur.close()
            close_conn(conn)
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