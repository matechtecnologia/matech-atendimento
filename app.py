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
from gemini import gerar_resposta, gerar_prompt_vendedor, validar_nicho_ia, gerar_prompt_personalizado
from plano_install import instalar_plano
from consultor_install import instalar_consultor
from asaas import criar_cliente, criar_cobranca_pix, obter_qr_code, consultar_pagamento
from plano_rotas import registrar_rotas_plano
from plano_estrategico import inicializar_plano_estrategico

load_dotenv()

app = FastAPI(title="M.A Tech")

# ===== SEGURANCA: SESSAO ASSINADA =====
# O navegador NAO pode mais dizer quem ele e. Os cookies usuario_id e usuario_tipo
# enviados pelo navegador sao descartados; so vale o cookie assinado "sessao".
import hmac as _hmac
import hashlib as _hashlib
import time as _time
import secrets as _secrets

SECRET_KEY = os.getenv("SECRET_KEY") or _secrets.token_hex(32)
if not os.getenv("SECRET_KEY"):
    print("AVISO: SECRET_KEY nao definida. Defina no Render, senao todos saem do login a cada reinicio.")
_COOKIE_SECURE = bool(os.getenv("RENDER"))
_SESSAO_DURACAO = 60 * 60 * 24 * 7


def assinar_sessao(uid, tipo):
    exp = int(_time.time()) + _SESSAO_DURACAO
    base = f"{int(uid)}.{tipo}.{exp}"
    sig = _hmac.new(SECRET_KEY.encode(), base.encode(), _hashlib.sha256).hexdigest()
    return f"{base}.{sig}"


def ler_sessao(valor):
    try:
        uid, tipo, exp, sig = (valor or "").split(".")
        base = f"{uid}.{tipo}.{exp}"
        esperado = _hmac.new(SECRET_KEY.encode(), base.encode(), _hashlib.sha256).hexdigest()
        if not _hmac.compare_digest(sig, esperado):
            return None
        if int(exp) < _time.time():
            return None
        return uid, tipo
    except Exception:
        return None


class AuthCookieMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            partes_cookie = []
            for k, v in scope["headers"]:
                if k == b"cookie":
                    for parte in v.decode("latin-1").split(";"):
                        parte = parte.strip()
                        if parte:
                            partes_cookie.append(parte)
            sessao = None
            mantidos = []
            for parte in partes_cookie:
                nome, _, valor = parte.partition("=")
                nome = nome.strip()
                if nome == "sessao":
                    sessao = valor.strip()
                elif nome not in ("usuario_id", "usuario_tipo"):
                    mantidos.append(parte)
            dados = ler_sessao(sessao) if sessao else None
            if dados:
                mantidos.append(f"usuario_id={dados[0]}")
                mantidos.append(f"usuario_tipo={dados[1]}")
            novos = [(k, v) for k, v in scope["headers"] if k != b"cookie"]
            if mantidos:
                novos.append((b"cookie", "; ".join(mantidos).encode("latin-1")))
            scope = dict(scope)
            scope["headers"] = novos
        await self.app(scope, receive, send)


app.add_middleware(AuthCookieMiddleware)
# Static com cache control
from starlette.staticfiles import StaticFiles as _SF
from starlette.responses import Response as _Resp

class _CacheStatic(_SF):
    async def get_response(self, path, scope):
        resp = await super().get_response(path, scope)
        if resp.status_code == 200:
            resp.headers["Cache-Control"] = "public, max-age=86400"
        return resp

app.mount("/static", _CacheStatic(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

LIMITES = {"gratis": 1, "basico": 3, "pro": 10, "empresarial": 25}
PLANOS_PRECO = {"basico": 97.0, "pro": 297.0, "empresarial": 597.0}
LIMITES_RESPOSTAS = {"gratis": 300, "basico": 3000, "pro": 10000, "empresarial": 30000}
EXCEDENTE_PRECO = {"gratis": 0.0, "basico": 0.05, "pro": 0.04, "empresarial": 0.03}
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
    cur.execute("""CREATE TABLE IF NOT EXISTS followups (
        id SERIAL PRIMARY KEY,
        vendedor_id INTEGER NOT NULL,
        cliente_id INTEGER NOT NULL,
        tipo TEXT NOT NULL,
        data_agendada DATE NOT NULL,
        feito BOOLEAN DEFAULT FALSE,
        feito_em TIMESTAMP WITH TIME ZONE,
        observacao TEXT,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("CREATE INDEX IF NOT EXISTS idx_followups_vendedor ON followups(vendedor_id, data_agendada, feito)")

    cur.execute("""CREATE TABLE IF NOT EXISTS leads_landing (
        id SERIAL PRIMARY KEY,
        nome TEXT,
        whatsapp TEXT NOT NULL,
        email TEXT,
        ip TEXT,
        convertido BOOLEAN DEFAULT FALSE,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("CREATE INDEX IF NOT EXISTS idx_leads_landing_wpp ON leads_landing(whatsapp)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_leads_landing_data ON leads_landing(criado_em DESC)")

    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='vendedores'")
    cols_v = [r[0] for r in cur.fetchall()]
    if 'followup_snooze_ate' not in cols_v:
        cur.execute('ALTER TABLE vendedores ADD COLUMN followup_snooze_ate TIMESTAMP WITH TIME ZONE')

    cur.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name='vendedores' AND column_name='codigo_indicacao') THEN
                ALTER TABLE vendedores ADD COLUMN codigo_indicacao TEXT UNIQUE;
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name='vendedores' AND column_name='indicado_por') THEN
                ALTER TABLE vendedores ADD COLUMN indicado_por INTEGER;
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name='vendedores' AND column_name='indicacao_recompensada') THEN
                ALTER TABLE vendedores ADD COLUMN indicacao_recompensada BOOLEAN DEFAULT FALSE;
            END IF;
        END $$;
    """)

    cur.execute("""CREATE TABLE IF NOT EXISTS indicacoes (
        id SERIAL PRIMARY KEY,
        indicador_id INTEGER NOT NULL,
        indicado_id INTEGER NOT NULL,
        codigo TEXT NOT NULL,
        recompensado BOOLEAN DEFAULT FALSE,
        recompensado_em TIMESTAMP WITH TIME ZONE,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("CREATE INDEX IF NOT EXISTS idx_indicacoes_indicador ON indicacoes(indicador_id)")

    cur.execute("""CREATE TABLE IF NOT EXISTS tentativas_login (
        id SERIAL PRIMARY KEY,
        email TEXT NOT NULL,
        ip TEXT,
        sucesso BOOLEAN DEFAULT FALSE,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("CREATE INDEX IF NOT EXISTS idx_tentativas_login ON tentativas_login(email, criado_em DESC)")

    cur.execute("CREATE INDEX IF NOT EXISTS idx_clientes_vendedor ON clientes(vendedor_id)")

    cur.execute('''CREATE TABLE IF NOT EXISTS respostas_ia (
        id SERIAL PRIMARY KEY,
        vendedor_id INTEGER NOT NULL,
        mes_ano TEXT NOT NULL,
        total INTEGER DEFAULT 0,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(vendedor_id, mes_ano)
    )''')

    cur.execute("CREATE INDEX IF NOT EXISTS idx_respostas_ia_vendedor ON respostas_ia(vendedor_id, mes_ano)")

    _adm_email = os.getenv("ADMIN_EMAIL")
    _adm_senha = os.getenv("ADMIN_SENHA_INICIAL")
    if _adm_email and _adm_senha:
        cur.execute("SELECT id FROM usuarios WHERE email = %s", (_adm_email,))
        if not cur.fetchone():
            h = pwd_context.hash(_adm_senha)
            cur.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES (%s, %s, %s, 'admin')", ("Admin M.A Tech", _adm_email, h))

    conn.commit()
    cur.close()
    close_conn(conn)
print("Banco inicializado")


try:
    inicializar_banco()
except Exception as e:
    print(f"Erro ao inicializar banco: {e}")

try:
    instalar_plano(app, get_conn, close_conn, Cookie, Request)
except Exception as e:
    print(f'Erro ao instalar plano: {e}')

try:
    instalar_consultor(app, get_conn, close_conn, Cookie, Request)
except Exception as e:
    print(f'Erro ao instalar consultor: {e}')


# inicializar_plano_estrategico DESATIVADO (apagava as tabelas a cada restart)
# Quem cria as tabelas agora e o plano_db.py via plano_install.py
# try:
#     inicializar_plano_estrategico(get_conn, close_conn)
# except Exception as e:
#     print(f"Erro ao inicializar plano estrategico: {e}")


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
                SELECT u.id, u.nome, u.email, u.whatsapp, u.criado_em, v.plano, v.id as vendedor_id,
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




def _mes_ano_atual():
    from datetime import datetime as _dt
    return _dt.now().strftime("%Y-%m")


def contar_respostas_mes(vendedor_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT total FROM respostas_ia WHERE vendedor_id = %s AND mes_ano = %s", (vendedor_id, _mes_ano_atual()))
    r = cur.fetchone()
    cur.close()
    close_conn(conn)
    return r[0] if r else 0


def incrementar_resposta(vendedor_id):
    conn = get_conn()
    cur = conn.cursor()
    mes = _mes_ano_atual()
    cur.execute("""INSERT INTO respostas_ia (vendedor_id, mes_ano, total)
                   VALUES (%s, %s, 1)
                   ON CONFLICT (vendedor_id, mes_ano)
                   DO UPDATE SET total = respostas_ia.total + 1, atualizado_em = CURRENT_TIMESTAMP""",
                (vendedor_id, mes))
    conn.commit()
    cur.close()
    close_conn(conn)


def processar_atendimento(aid, linha_crm, mensagem, prompt, hist, whatsapp, uid, cid=None, nicho_dict=None):
    try:
        r = gerar_resposta(linha_crm, mensagem, prompt, hist, nicho_dict=nicho_dict)
        salvar_historico(whatsapp, uid, "ia", r.get("o_que_falar", ""))
        try:
            incrementar_resposta(uid)
        except Exception as _e:
            print("Erro incrementar resposta:", _e)
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE atendimentos SET o_que_falar=%s, texto_para_enviar=%s, acao_crm=%s, linha_crm_gerada=%s, status='pronto' WHERE id=%s", (r.get("o_que_falar", ""), r.get("texto_para_enviar", ""), r.get("estagio", "Em Atendimento"), r.get("linha_crm", ""), aid))
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
def fazer_signup(request: Request, nome: str = Form(...), email: str = Form(...), senha: str = Form(...), whatsapp: str = Form(...), ref: str = Form("")):
    ip = obter_ip(request)

    if contar_signups_ip(ip, 1) >= 3:
        return RedirectResponse(url="/signup?erro=Muitas+contas+criadas+nesse+IP.+Tente+em+1+hora", status_code=303)

    wpp_limpo, erro_wpp = validar_whatsapp(whatsapp)
    if erro_wpp:
        return RedirectResponse(url=f"/signup?erro={erro_wpp}", status_code=303)

    registrar_tentativa_ip(ip)

    ok, msg, uid = criar_vendedor_v2(nome, email, senha, wpp_limpo)
    if not ok:
        return RedirectResponse(url=f"/signup?erro={msg}", status_code=303)

    # Registra indicacao se tiver codigo
    if ref:
        try:
            v_novo = buscar_vendedor(uid)
            if v_novo:
                registrar_indicacao(ref, v_novo["id"])
        except Exception as e:
            print(f"Erro registrar indicacao: {e}")

    return RedirectResponse(url="/login?criado=1", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def tela_login(request: Request, erro: str = None):
    return templates.TemplateResponse(request=request, name="login.html", context={"erro": erro})


@app.post("/login")
def fazer_login(request: Request, email: str = Form(...), senha: str = Form(...)):
    ip = obter_ip(request)

    # Rate limit: max 5 tentativas falhas em 15 min
    if contar_tentativas_login(email, ip, 5) >= 5:
        return RedirectResponse(url="/login?erro=Muitas tentativas. Aguarde 5 minutos.", status_code=303)

    u = buscar_usuario(email)
    if not u:
        registrar_tentativa_login(email, ip, False)
        return RedirectResponse(url="/login?erro=Usuario nao encontrado", status_code=303)
    if not pwd_context.verify(senha, u["senha"]):
        registrar_tentativa_login(email, ip, False)
        return RedirectResponse(url="/login?erro=Senha incorreta", status_code=303)

    # Login OK
    registrar_tentativa_login(email, ip, True)
    v = buscar_vendedor(u["id"])
    if v:
        verificar_expiracao(v["id"])
    if u["tipo"] == "admin":
        destino = "/admin"
    else:
        v = buscar_vendedor(u["id"])
        destino = "/hub"
    r = RedirectResponse(url=destino, status_code=303)
    r.set_cookie(key="usuario_nome", value=u["nome"], httponly=True, samesite="lax", secure=_COOKIE_SECURE)
    r.set_cookie(key="sessao", value=assinar_sessao(u["id"], u["tipo"]), httponly=True, samesite="lax", secure=_COOKIE_SECURE, max_age=_SESSAO_DURACAO)
    return r


@app.get("/hub", response_class=HTMLResponse)
def tela_hub(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    # Destino da area ativa
    if not v["onboarding_completo"]:
        area_url = "/onboarding"
    else:
        area_url = "/clientes"
    return templates.TemplateResponse(request=request, name="hub.html", context={
        "usuario_nome": usuario_nome,
        "usuario_tipo": usuario_tipo,
        "area_ativa_url": area_url,
    })


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

    erro_respostas = validar_respostas_onboarding(produto, publico, preco, dor, objecao, diferencial, tom)
    if erro_respostas:
        from urllib.parse import quote
        return RedirectResponse(url=f"/onboarding?erro={quote(erro_respostas)}", status_code=303)

    valido, motivo = validar_nicho_simples(nome_nicho, produto)
    if not valido:
        from urllib.parse import quote
        return RedirectResponse(url=f"/onboarding?erro={quote(motivo)}", status_code=303)

    pg = gerar_prompt_personalizado(nome_nicho, produto, publico, preco, dor, objecao, diferencial, tom)
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
    return RedirectResponse(url="/bem-vindo", status_code=303)


@app.get("/consultoria", response_class=HTMLResponse)
def tela_consultoria(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    icone = '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>'
    return templates.TemplateResponse(request, "consultoria.html", {
        "usuario_nome": usuario_nome or "",
        "usuario_tipo": usuario_tipo or "",
        "icone_briefcase": icone
    })

@app.get("/clientes", response_class=HTMLResponse)
def tela_clientes(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None), nicho_id: int = None, nicho_cookie: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, nome FROM nichos WHERE vendedor_id = %s AND ativo = TRUE ORDER BY id", (v["id"],))
    nichos = [dict(n) for n in cur.fetchall()]
    if not nichos:
        cur.close()
        close_conn(conn)
        return RedirectResponse(url="/onboarding")
    ids_ok = [n["id"] for n in nichos]
    nicho_atual = None
    if nicho_id and nicho_id in ids_ok:
        nicho_atual = nicho_id
    elif nicho_cookie:
        try:
            ci = int(nicho_cookie)
            if ci in ids_ok:
                nicho_atual = ci
        except Exception:
            pass
    if not nicho_atual:
        nicho_atual = nichos[0]["id"]
    cur.execute("SELECT * FROM clientes WHERE vendedor_id = %s AND nicho_id = %s ORDER BY atualizado_em DESC", (v["id"], nicho_atual))
    clientes = [dict(c) for c in cur.fetchall()]
    cur.close()
    close_conn(conn)
    resp = templates.TemplateResponse(request=request, name="clientes.html", context={
        "usuario_nome": usuario_nome,
        "usuario_tipo": usuario_tipo,
        "total_followups": _total_followups_para_template(usuario_id),
        "clientes": clientes,
        "nichos": nichos,
        "nicho_atual": nicho_atual,
    })
    resp.set_cookie(key="nicho_cookie", value=str(nicho_atual), max_age=60*60*24*30, samesite="lax")
    resp.set_cookie(key="nicho_js", value=str(nicho_atual), max_age=60*60*24*30, samesite="lax")
    return resp


@app.post("/salvar_cliente_manual")
def salvar_cliente_manual(whatsapp: str = Form(...), nome: str = Form(...), email: str = Form(""), origem: str = Form(""), status: str = Form("novo lead"), observacoes: str = Form(""), usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    salvar_cliente(v["id"], whatsapp, nome, email, origem, status, observacoes)
    return RedirectResponse(url="/clientes", status_code=303)


@app.get("/cliente/novo", response_class=HTMLResponse)
def tela_novo_cliente(request: Request, nicho_id: int = None, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None), erro: str = None):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    if not nicho_id:
        return RedirectResponse(url="/clientes")
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, nome FROM nichos WHERE id = %s AND vendedor_id = %s AND ativo = TRUE", (nicho_id, v["id"]))
    nicho = cur.fetchone()
    cur.close()
    close_conn(conn)
    if not nicho:
        return RedirectResponse(url="/clientes")
    return templates.TemplateResponse(request=request, name="novo_cliente.html", context={
        "usuario_nome": usuario_nome,
        "usuario_tipo": usuario_tipo,
        "total_followups": _total_followups_para_template(usuario_id),
        "nicho": dict(nicho),
        "erro": erro,
    })


@app.post("/cliente/novo")
def salvar_novo_cliente(nicho_id: int = Form(...), whatsapp: str = Form(...), nome: str = Form(...), email: str = Form(""), origem: str = Form(""), status: str = Form("novo lead"), observacoes: str = Form(""), usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM nichos WHERE id = %s AND vendedor_id = %s AND ativo = TRUE", (nicho_id, v["id"]))
    if not cur.fetchone():
        cur.close()
        close_conn(conn)
        return RedirectResponse(url="/clientes", status_code=303)
    cur.close()
    close_conn(conn)
    wpp_limpo, err = validar_whatsapp(whatsapp)
    if err:
        from urllib.parse import quote
        return RedirectResponse(url="/cliente/novo?nicho_id=" + str(nicho_id) + "&erro=" + quote(err), status_code=303)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM clientes WHERE whatsapp = %s AND vendedor_id = %s", (wpp_limpo, v["id"]))
    if cur.fetchone():
        cur.close()
        close_conn(conn)
        from urllib.parse import quote
        return RedirectResponse(url="/cliente/novo?nicho_id=" + str(nicho_id) + "&erro=" + quote("WhatsApp ja cadastrado"), status_code=303)
    cur.close()
    close_conn(conn)
    salvar_cliente(v["id"], wpp_limpo, nome, email, origem, status, observacoes, "", nicho_id)
    return RedirectResponse(url="/clientes?nicho_id=" + str(nicho_id), status_code=303)


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
    if not cli["nicho_id"]:
        return RedirectResponse(url="/clientes")
    conn2 = get_conn()
    cur2 = conn2.cursor(cursor_factory=RealDictCursor)
    cur2.execute("SELECT * FROM nichos WHERE id = %s AND vendedor_id = %s AND ativo = TRUE", (cli["nicho_id"], v["id"]))
    nicho = cur2.fetchone()
    cur2.close()
    close_conn(conn2)
    if not nicho:
        return RedirectResponse(url="/clientes")
    return templates.TemplateResponse(request=request, name="atendimento_cliente.html", context={"usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo, "total_followups": _total_followups_para_template(usuario_id), "cliente": dict(cli), "nicho": dict(nicho)})


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
        # Busca o historico completo pelo whatsapp + vendedor
        cur.execute("""
            SELECT id, direcao, mensagem, criado_em
            FROM historico
            WHERE whatsapp = %s AND vendedor_id = %s
            ORDER BY id ASC
        """, (cli["whatsapp"], v["id"]))
        hist = [dict(h) for h in cur.fetchall()]

    cur.close()
    close_conn(conn)

    if not cli:
        return RedirectResponse(url="/clientes")

    return templates.TemplateResponse(request=request, name="cliente_detalhe.html", context={
        "usuario_nome": usuario_nome,
        "usuario_tipo": usuario_tipo,
        "total_followups": _total_followups_para_template(usuario_id),
        "cliente": dict(cli),
        "historico": hist
    })


@app.post("/gerar_resposta")
def rota_gerar_resposta(whatsapp: str = Form(...), nicho_id: int = Form(...), mensagem_cliente: str = Form(...), cliente_id: int = Form(None), modo_instrucao: str = Form(None), usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")

    vendedor_atual = buscar_vendedor(usuario_id)
    if not vendedor_atual:
        return RedirectResponse(url="/onboarding")
    vid_real = vendedor_atual["id"]

    if not mensagem_cliente or len(mensagem_cliente.strip()) < 3:
        return RedirectResponse(url=f"/cliente/{cliente_id}/atender?erro=Mensagem+muito+curta+(minimo+3+caracteres)", status_code=303)

    if modo_instrucao:
        mensagem_cliente = f"""### INSTRUCAO DIRETA DO VENDEDOR ###

ATENCAO IA: o texto abaixo NAO e uma fala do cliente.
E uma ORDEM do vendedor pra voce executar.

NAO responda como se voce fosse o cliente.
NAO trate isso como nova mensagem do cliente.
EXECUTE essa instrucao e gere a proxima resposta do vendedor.

INSTRUCAO A EXECUTAR:
{mensagem_cliente}

### FIM DA INSTRUCAO ###"""
        # Marca no historico como INSTRUCAO, nao como fala do cliente
        salvar_historico(whatsapp, vid_real, "instrucao", f"[INSTRUCAO] {mensagem_cliente}")

    n = buscar_nicho(nicho_id)
    if not n or n["vendedor_id"] != vid_real:
        return RedirectResponse(url="/clientes")

    # Usa o prompt personalizado que foi gerado pela IA e salvo no banco
    prompt_atualizado = n.get("prompt_gerado") or ""
    if not prompt_atualizado:
        # Se por algum motivo nao tiver, gera na hora
        prompt_atualizado = gerar_prompt_personalizado(
            n.get("nome") or "",
            n.get("produto") or "",
            n.get("publico") or "",
            n.get("preco") or "",
            n.get("dor") or "",
            n.get("objecao") or "",
            n.get("diferencial") or "",
            n.get("tom") or ""
        )

    linha_crm = ""
    if cliente_id:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT linha_crm FROM clientes WHERE id = %s AND vendedor_id = %s", (cliente_id, vid_real))
        cli = cur.fetchone()
        cur.close()
        close_conn(conn)
        if cli:
            linha_crm = cli["linha_crm"] or ""
        else:
            cliente_id = None

    hist = buscar_historico(whatsapp, vid_real)

    if not modo_instrucao:
        salvar_historico(whatsapp, vid_real, "cliente", mensagem_cliente)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO atendimentos (atendente_id, nicho_id, whatsapp, linha_crm, mensagem_cliente, cliente_id, status) VALUES (%s, %s, %s, %s, %s, %s, 'processando') RETURNING id", (usuario_id, nicho_id, whatsapp, linha_crm, mensagem_cliente, cliente_id))
    aid = cur.fetchone()[0]
    conn.commit()
    cur.close()
    close_conn(conn)

    # Verifica limite mensal de respostas
    try:
        usadas = contar_respostas_mes(vid_real)
        limite = LIMITES_RESPOSTAS.get(vendedor_atual["plano"], 300)
        if usadas >= limite:
            return RedirectResponse(url="/planos?erro=Limite+de+respostas+atingido.+Faca+upgrade", status_code=303)
    except Exception as _e:
        print("Erro verificar limite:", _e)

    threading.Thread(target=processar_atendimento, args=(aid, linha_crm, mensagem_cliente, prompt_atualizado, hist, whatsapp, vid_real, cliente_id), kwargs={"nicho_dict": dict(n)}).start()
    return RedirectResponse(url=f"/resultado/{aid}", status_code=303)


@app.get("/resultado/{atendimento_id}", response_class=HTMLResponse)
def tela_resultado(request: Request, atendimento_id: int, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM atendimentos WHERE id = %s AND atendente_id = %s", (atendimento_id, int(usuario_id)))
    a = cur.fetchone()
    cur.close()
    close_conn(conn)
    if not a:
        return RedirectResponse(url="/clientes")
    return templates.TemplateResponse(request=request, name="resultado.html", context={"usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo, "total_followups": _total_followups_para_template(usuario_id), "atendimento": dict(a)})


@app.post("/salvar_atendimento_como_cliente/{atendimento_id}")
def salvar_atendimento_como_cliente(atendimento_id: int, usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM atendimentos WHERE id = %s AND atendente_id = %s", (atendimento_id, int(usuario_id)))
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
    return templates.TemplateResponse(request=request, name="meus_nichos.html", context={"usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo, "total_followups": _total_followups_para_template(usuario_id), "nichos": [dict(n) for n in ns], "total": len(ns), "limite": LIMITES.get(v["plano"], 1), "plano": v["plano"], "erro": erro})


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

    erro_respostas = validar_respostas_onboarding(produto, publico, preco, dor, objecao, diferencial, tom)
    if erro_respostas:
        from urllib.parse import quote
        return RedirectResponse(url=f"/novo_nicho?erro={quote(erro_respostas)}", status_code=303)

    valido, motivo = validar_nicho_simples(nome_nicho, produto)
    if not valido:
        from urllib.parse import quote
        return RedirectResponse(url=f"/novo_nicho?erro={quote(motivo)}", status_code=303)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM nichos WHERE vendedor_id = %s AND LOWER(nome) = LOWER(%s)", (v["id"], nome_nicho.strip()))
    if cur.fetchone():
        cur.close()
        close_conn(conn)
        from urllib.parse import quote
        return RedirectResponse(url=f"/novo_nicho?erro={quote('Voce ja tem um nicho com esse nome.')}", status_code=303)
    cur.close()
    close_conn(conn)

    pg = gerar_prompt_personalizado(nome_nicho, produto, publico, preco, dor, objecao, diferencial, tom)
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
    respostas_usadas = contar_respostas_mes(v["id"])
    respostas_limite = LIMITES_RESPOSTAS.get(v["plano"], 300)
    return templates.TemplateResponse(request=request, name="planos.html", context={"usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo, "total_followups": _total_followups_para_template(usuario_id), "plano_atual": v["plano"], "dias_restantes": d, "respostas_usadas": respostas_usadas, "respostas_limite": respostas_limite})


@app.post("/assinar")
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
    return templates.TemplateResponse(request=request, name="assinar.html", context={"usuario_nome": usuario_nome, "plano": plano, "valor": valor, "erro": None})


@app.post("/gerar_pix")
def gerar_pix(request: Request, plano: str = Form(...), valor: str = Form(...), cpf_cnpj: str = Form(...), usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None)):
    plano = (plano or "").lower().strip()
    if plano not in PLANOS_PRECO:
        return RedirectResponse(url="/planos", status_code=303)
    valor = f"{PLANOS_PRECO[plano]:.2f}"
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
    cur.execute("SELECT plano, valor, status FROM pagamentos WHERE payment_id = %s AND vendedor_id = (SELECT id FROM vendedores WHERE usuario_id = %s)", (payment_id, int(usuario_id)))
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
            # Recompensa quem indicou
            try:
                recompensar_indicador(row[0])
            except Exception as e:
                print(f"Erro recompensar indicador: {e}")
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
        info_real = consultar_pagamento(pid) if pid else None
        confirmado = bool(info_real) and info_real.get("status") in ["CONFIRMED", "RECEIVED"]
        if ev in ["PAYMENT_CONFIRMED", "PAYMENT_RECEIVED"] and confirmado:
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
    r.delete_cookie("sessao")
    return r



# ============ CRM â€” CLIENTES (editar/excluir) ============

def buscar_cliente(cid, vid):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM clientes WHERE id = %s AND vendedor_id = %s", (cid, vid))
    c = cur.fetchone()
    cur.close()
    close_conn(conn)
    return c


def atualizar_cliente(cid, vid, whatsapp, nome, email, origem, status, obs):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT whatsapp FROM clientes WHERE id = %s AND vendedor_id = %s", (cid, vid))
    row = cur.fetchone()
    if not row:
        cur.close()
        close_conn(conn)
        return False, "Cliente nao encontrado"
    old_wpp = row[0]
    cur.execute("SELECT id FROM clientes WHERE whatsapp = %s AND vendedor_id = %s AND id != %s", (whatsapp, vid, cid))
    if cur.fetchone():
        cur.close()
        close_conn(conn)
        return False, "Ja existe outro cliente com esse WhatsApp"
    cur.execute("UPDATE clientes SET whatsapp=%s, nome=%s, email=%s, origem=%s, status=%s, observacoes=%s, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s AND vendedor_id=%s", (whatsapp, nome, email, origem, status, obs, cid, vid))
    if old_wpp != whatsapp:
        cur.execute("UPDATE historico SET whatsapp=%s WHERE whatsapp=%s AND vendedor_id=%s", (whatsapp, old_wpp, vid))
    conn.commit()
    cur.close()
    close_conn(conn)
    return True, "OK"


def excluir_cliente(cid, vid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT whatsapp FROM clientes WHERE id = %s AND vendedor_id = %s", (cid, vid))
    row = cur.fetchone()
    if not row:
        cur.close()
        close_conn(conn)
        return False
    wpp = row[0]
    cur.execute("DELETE FROM clientes WHERE id = %s AND vendedor_id = %s", (cid, vid))
    cur.execute("DELETE FROM historico WHERE whatsapp = %s AND vendedor_id = %s", (wpp, vid))
    cur.execute("DELETE FROM atendimentos WHERE cliente_id = %s", (cid,))
    conn.commit()
    cur.close()
    close_conn(conn)
    return True


@app.post("/cliente/{cliente_id}/editar")
def rota_editar_cliente(cliente_id: int, whatsapp: str = Form(...), nome: str = Form(...), email: str = Form(""), origem: str = Form(""), status: str = Form("novo lead"), observacoes: str = Form(""), usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    ok, msg = atualizar_cliente(cliente_id, v["id"], whatsapp, nome, email, origem, status, observacoes)
    if not ok:
        return RedirectResponse(url=f"/cliente/{cliente_id}?erro={msg}", status_code=303)
    return RedirectResponse(url=f"/cliente/{cliente_id}?ok=1", status_code=303)


@app.post("/cliente/{cliente_id}/excluir")
def rota_excluir_cliente(cliente_id: int, usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    excluir_cliente(cliente_id, v["id"])
    return RedirectResponse(url="/clientes?excluido=1", status_code=303)


# ============ ADMIN â€” GESTÃƒO DE VENDEDORES ============

def buscar_vendedor_admin(vid):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT v.id as vendedor_id, v.plano, v.plano_expira_em, v.onboarding_completo, v.criado_em as v_criado_em,
               u.id as usuario_id, u.nome, u.email, u.whatsapp, u.tipo, u.ativo, u.criado_em as u_criado_em
        FROM vendedores v JOIN usuarios u ON u.id = v.usuario_id
        WHERE v.id = %s
    """, (vid,))
    r = cur.fetchone()
    cur.close()
    close_conn(conn)
    return r


@app.get("/admin/vendedor/{vendedor_id}", response_class=HTMLResponse)
def admin_detalhe_vendedor(request: Request, vendedor_id: int, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None), erro: str = None, ok: str = None):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    v = buscar_vendedor_admin(vendedor_id)
    if not v:
        return RedirectResponse(url="/admin")
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM clientes WHERE vendedor_id = %s ORDER BY atualizado_em DESC", (vendedor_id,))
    clientes = [dict(c) for c in cur.fetchall()]
    cur.execute("SELECT * FROM nichos WHERE vendedor_id = %s ORDER BY id", (vendedor_id,))
    nichos = [dict(n) for n in cur.fetchall()]
    cur.execute("SELECT COUNT(*) as t FROM atendimentos WHERE atendente_id = %s", (v["usuario_id"],))
    total_atend = cur.fetchone()["t"]
    cur.close()
    close_conn(conn)
    return templates.TemplateResponse(request=request, name="admin_vendedor.html", context={
        "usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo, "total_followups": _total_followups_para_template(usuario_id),
        "v": dict(v), "clientes": clientes, "nichos": nichos, "total_atend": total_atend,
        "erro": erro, "ok": ok
    })


@app.post("/admin/vendedor/{vendedor_id}/editar")
def admin_editar_vendedor(vendedor_id: int, nome: str = Form(...), email: str = Form(...), usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    v = buscar_vendedor_admin(vendedor_id)
    if not v:
        return RedirectResponse(url="/admin")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE email = %s AND id != %s", (email, v["usuario_id"]))
    if cur.fetchone():
        cur.close()
        close_conn(conn)
        return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}?erro=Email+ja+em+uso", status_code=303)
    cur.execute("UPDATE usuarios SET nome=%s, email=%s WHERE id=%s", (nome, email, v["usuario_id"]))
    conn.commit()
    cur.close()
    close_conn(conn)
    return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}?ok=1", status_code=303)


@app.post("/admin/vendedor/{vendedor_id}/bloquear")
def admin_bloquear_vendedor(vendedor_id: int, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    v = buscar_vendedor_admin(vendedor_id)
    if not v:
        return RedirectResponse(url="/admin")
    conn = get_conn()
    cur = conn.cursor()
    novo = not v["ativo"]
    cur.execute("UPDATE usuarios SET ativo=%s WHERE id=%s", (novo, v["usuario_id"]))
    conn.commit()
    cur.close()
    close_conn(conn)
    return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}?ok=1", status_code=303)


@app.post("/admin/vendedor/{vendedor_id}/plano")
def admin_mudar_plano_vendedor(vendedor_id: int, plano: str = Form(...), usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    conn = get_conn()
    cur = conn.cursor()
    if plano == "gratis":
        cur.execute("UPDATE vendedores SET plano=%s, plano_expira_em=NULL, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s", (plano, vendedor_id))
    else:
        exp = datetime.now() + timedelta(days=30)
        cur.execute("UPDATE vendedores SET plano=%s, plano_expira_em=%s, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s", (plano, exp, vendedor_id))
    conn.commit()
    cur.close()
    close_conn(conn)
    return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}?ok=1", status_code=303)


@app.post("/admin/vendedor/{vendedor_id}/excluir")
def admin_excluir_vendedor(vendedor_id: int, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    v = buscar_vendedor_admin(vendedor_id)
    if not v:
        return RedirectResponse(url="/admin")
    conn = get_conn()
    cur = conn.cursor()
    uid = v["usuario_id"]
    cur.execute("DELETE FROM historico WHERE vendedor_id=%s", (vendedor_id,))
    cur.execute("DELETE FROM atendimentos WHERE atendente_id=%s", (uid,))
    cur.execute("DELETE FROM clientes WHERE vendedor_id=%s", (vendedor_id,))
    cur.execute("DELETE FROM nichos WHERE vendedor_id=%s", (vendedor_id,))
    cur.execute("DELETE FROM pagamentos WHERE vendedor_id=%s", (vendedor_id,))
    cur.execute("DELETE FROM vendedores WHERE id=%s", (vendedor_id,))
    cur.execute("DELETE FROM usuarios WHERE id=%s", (uid,))
    conn.commit()
    cur.close()
    close_conn(conn)
    return RedirectResponse(url="/admin?excluido=1", status_code=303)


@app.get("/admin/criar", response_class=HTMLResponse)
def admin_criar_form(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None), erro: str = None):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request=request, name="admin_criar.html", context={"usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo, "total_followups": _total_followups_para_template(usuario_id), "erro": erro})


@app.post("/admin/criar")
def admin_criar_vendedor(nome: str = Form(...), email: str = Form(...), senha: str = Form(...), plano: str = Form("gratis"), usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    ok, msg = criar_vendedor(nome, email, senha)
    if not ok:
        return RedirectResponse(url=f"/admin/criar?erro={msg}", status_code=303)
    if plano != "gratis":
        conn = get_conn()
        cur = conn.cursor()
        exp = datetime.now() + timedelta(days=30)
        cur.execute("UPDATE vendedores SET plano=%s, plano_expira_em=%s WHERE usuario_id = (SELECT id FROM usuarios WHERE email=%s)", (plano, exp, email))
        conn.commit()
        cur.close()
        close_conn(conn)
    return RedirectResponse(url="/admin", status_code=303)



# ============ FAVICON ============

from fastapi.responses import FileResponse

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse("static/favicon.svg", media_type="image/svg+xml")



# ============ RELATÃ“RIOS ============

@app.get("/relatorios", response_class=HTMLResponse)
def tela_relatorios(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    vid = v["id"]

    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Clientes por status
    cur.execute("SELECT status, COUNT(*) as qtd FROM clientes WHERE vendedor_id = %s GROUP BY status", (vid,))
    por_status = {}
    for r in cur.fetchall():
        s = (r["status"] or "novo lead").lower()
        por_status[s] = r["qtd"]

    total = sum(por_status.values())
    novos = por_status.get("novo lead", 0) + por_status.get("lead", 0)
    em_neg = por_status.get("negociaÃ§Ã£o", 0) + por_status.get("negociacao", 0) + por_status.get("negociando", 0)
    em_atend = por_status.get("em atendimento", 0)
    ganhos = por_status.get("cliente", 0)
    perdidos = por_status.get("perdido", 0)

    # Clientes por origem (top 5)
    cur.execute("""
        SELECT COALESCE(NULLIF(TRIM(origem), ''), 'NÃ£o informada') as origem, COUNT(*) as qtd
        FROM clientes WHERE vendedor_id = %s
        GROUP BY origem ORDER BY qtd DESC LIMIT 5
    """, (vid,))
    top_origens = [dict(r) for r in cur.fetchall()]

    # Atividade Ãºltimos 7 dias (atendimentos por dia)
    cur.execute("""
        SELECT DATE(criado_em) as dia, COUNT(*) as qtd
        FROM atendimentos
        WHERE atendente_id = %s AND criado_em >= CURRENT_DATE - INTERVAL '6 days'
        GROUP BY DATE(criado_em) ORDER BY dia
    """, (usuario_id,))
    atividade_raw = {str(r["dia"]): r["qtd"] for r in cur.fetchall()}

    from datetime import date, timedelta
    atividade = []
    hoje = date.today()
    for i in range(6, -1, -1):
        d = hoje - timedelta(days=i)
        atividade.append({
            "curto": ["Seg","Ter","Qua","Qui","Sex","SÃ¡b","Dom"][d.weekday()],
            "data": d.strftime("%d/%m"),
            "qtd": atividade_raw.get(str(d), 0)
        })
    max_atividade = max([a["qtd"] for a in atividade] + [1])
    total_atividade = sum(a["qtd"] for a in atividade)

    # Top clientes (mais atendidos)
    cur.execute("""
        SELECT c.nome, c.whatsapp, c.status, COUNT(a.id) as qtd
        FROM clientes c
        LEFT JOIN atendimentos a ON a.cliente_id = c.id
        WHERE c.vendedor_id = %s
        GROUP BY c.id, c.nome, c.whatsapp, c.status
        ORDER BY qtd DESC LIMIT 5
    """, (vid,))
    top_clientes = [dict(r) for r in cur.fetchall() if r["qtd"] > 0]

    # Top nichos
    cur.execute("""
        SELECT n.nome, COUNT(a.id) as qtd
        FROM nichos n
        LEFT JOIN atendimentos a ON a.nicho_id = n.id
        WHERE n.vendedor_id = %s
        GROUP BY n.id, n.nome ORDER BY qtd DESC LIMIT 5
    """, (vid,))
    top_nichos = [dict(r) for r in cur.fetchall() if r["qtd"] > 0]

    # Atendimentos totais (sÃ³ pra contexto)
    cur.execute("SELECT COUNT(*) as t FROM atendimentos WHERE atendente_id = %s", (usuario_id,))
    total_atend = cur.fetchone()["t"]

    cur.close()
    close_conn(conn)

    # MÃ©tricas calculadas
    clientes_ativos = novos + em_neg + em_atend
    taxa_conversao = round((ganhos / total * 100), 1) if total > 0 else 0
    media_atend_cliente = round(total_atend / total, 1) if total > 0 else 0

    # Percentuais do funil
    pct_novos = round((novos / total * 100), 0) if total > 0 else 0
    pct_neg = round(((em_neg + em_atend) / total * 100), 0) if total > 0 else 0
    pct_ganhos = round((ganhos / total * 100), 0) if total > 0 else 0
    pct_perdidos = round((perdidos / total * 100), 0) if total > 0 else 0

    return templates.TemplateResponse(request=request, name="relatorios.html", context={
        "usuario_nome": usuario_nome,
        "usuario_tipo": usuario_tipo, "total_followups": _total_followups_para_template(usuario_id),
        "total": total,
        "novos": novos,
        "em_neg": em_neg,
        "em_atend": em_atend,
        "ganhos": ganhos,
        "perdidos": perdidos,
        "total_atend": total_atend,
        "taxa_conversao": taxa_conversao,
        "media_atend_cliente": media_atend_cliente,
        "atividade": atividade,
        "max_atividade": max_atividade,
        "total_atividade": total_atividade,
        "top_origens": top_origens,
        "top_clientes": top_clientes,
        "top_nichos": top_nichos,
        "pct_novos": pct_novos,
        "pct_neg": pct_neg,
        "pct_ganhos": pct_ganhos,
        "pct_perdidos": pct_perdidos,
    })


# ============ ADMIN â€” EDITAR NICHOS E CLIENTES DO VENDEDOR ============

@app.post("/admin/vendedor/{vendedor_id}/nicho/{nicho_id}/editar")
def admin_editar_nicho(vendedor_id: int, nicho_id: int, nome: str = Form(...), produto: str = Form(""), publico: str = Form(""), preco: str = Form(""), dor: str = Form(""), objecao: str = Form(""), diferencial: str = Form(""), tom: str = Form(""), usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT vendedor_id FROM nichos WHERE id = %s", (nicho_id,))
    row = cur.fetchone()
    if not row or row[0] != vendedor_id:
        cur.close()
        close_conn(conn)
        return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}")
    pg = gerar_prompt_personalizado(nome, produto, publico, preco, dor, objecao, diferencial, tom)
    cur.execute("UPDATE nichos SET nome=%s, produto=%s, publico=%s, preco=%s, dor=%s, objecao=%s, diferencial=%s, tom=%s, prompt_gerado=%s WHERE id=%s",
                (nome, produto, publico, preco, dor, objecao, diferencial, tom, pg, nicho_id))
    conn.commit()
    cur.close()
    close_conn(conn)
    return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}?ok=1", status_code=303)


@app.post("/admin/vendedor/{vendedor_id}/nicho/{nicho_id}/excluir")
def admin_excluir_nicho(vendedor_id: int, nicho_id: int, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM nichos WHERE id = %s AND vendedor_id = %s", (nicho_id, vendedor_id))
    conn.commit()
    cur.close()
    close_conn(conn)
    return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}?ok=1", status_code=303)


@app.post("/admin/vendedor/{vendedor_id}/cliente/{cliente_id}/editar")
def admin_editar_cliente(vendedor_id: int, cliente_id: int, whatsapp: str = Form(...), nome: str = Form(...), email: str = Form(""), origem: str = Form(""), status: str = Form("novo lead"), observacoes: str = Form(""), usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT whatsapp FROM clientes WHERE id = %s AND vendedor_id = %s", (cliente_id, vendedor_id))
    row = cur.fetchone()
    if not row:
        cur.close()
        close_conn(conn)
        return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}")
    old_wpp = row[0]
    cur.execute("SELECT id FROM clientes WHERE whatsapp = %s AND vendedor_id = %s AND id != %s", (whatsapp, vendedor_id, cliente_id))
    if cur.fetchone():
        cur.close()
        close_conn(conn)
        return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}?erro=WhatsApp+ja+existe", status_code=303)
    cur.execute("UPDATE clientes SET whatsapp=%s, nome=%s, email=%s, origem=%s, status=%s, observacoes=%s, atualizado_em=CURRENT_TIMESTAMP WHERE id=%s AND vendedor_id=%s",
                (whatsapp, nome, email, origem, status, observacoes, cliente_id, vendedor_id))
    if old_wpp != whatsapp:
        cur.execute("UPDATE historico SET whatsapp=%s WHERE whatsapp=%s AND vendedor_id=%s", (whatsapp, old_wpp, vendedor_id))
    conn.commit()
    cur.close()
    close_conn(conn)
    return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}?ok=1", status_code=303)


@app.post("/admin/vendedor/{vendedor_id}/cliente/{cliente_id}/excluir")
def admin_excluir_cliente(vendedor_id: int, cliente_id: int, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT whatsapp FROM clientes WHERE id = %s AND vendedor_id = %s", (cliente_id, vendedor_id))
    row = cur.fetchone()
    if row:
        wpp = row[0]
        cur.execute("DELETE FROM clientes WHERE id = %s AND vendedor_id = %s", (cliente_id, vendedor_id))
        cur.execute("DELETE FROM historico WHERE whatsapp = %s AND vendedor_id = %s", (wpp, vendedor_id))
        cur.execute("DELETE FROM atendimentos WHERE cliente_id = %s", (cliente_id,))
    conn.commit()
    cur.close()
    close_conn(conn)
    return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}?ok=1", status_code=303)


@app.post("/admin/vendedor/{vendedor_id}/reset-onboarding")
def admin_reset_onboarding(vendedor_id: int, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE vendedores SET onboarding_completo = FALSE WHERE id = %s", (vendedor_id,))
    conn.commit()
    cur.close()
    close_conn(conn)
    return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}?ok=1", status_code=303)


@app.post("/admin/vendedor/{vendedor_id}/reset-senha")
def admin_reset_senha(vendedor_id: int, nova_senha: str = Form(...), usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    if len(nova_senha) < 6:
        return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}?erro=Senha+curta", status_code=303)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT usuario_id FROM vendedores WHERE id = %s", (vendedor_id,))
    row = cur.fetchone()
    if row:
        h = pwd_context.hash(nova_senha)
        cur.execute("UPDATE usuarios SET senha=%s WHERE id=%s", (h, row[0]))
        conn.commit()
    cur.close()
    close_conn(conn)
    return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}?ok=1", status_code=303)



# ============ ADMIN â€” HISTÃ“RICO E ATENDIMENTOS ============

@app.get("/admin/vendedor/{vendedor_id}/cliente/{cliente_id}/historico", response_class=HTMLResponse)
def admin_ver_historico(request: Request, vendedor_id: int, cliente_id: int, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    v = buscar_vendedor_admin(vendedor_id)
    if not v:
        return RedirectResponse(url="/admin")
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM clientes WHERE id = %s AND vendedor_id = %s", (cliente_id, vendedor_id))
    cli = cur.fetchone()
    if not cli:
        cur.close()
        close_conn(conn)
        return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}")
    cur.execute("SELECT * FROM historico WHERE whatsapp = %s AND vendedor_id = %s ORDER BY id ASC", (cli["whatsapp"], vendedor_id))
    hist = [dict(h) for h in cur.fetchall()]
    cur.execute("SELECT * FROM atendimentos WHERE cliente_id = %s ORDER BY id DESC", (cliente_id,))
    atends = [dict(a) for a in cur.fetchall()]
    cur.close()
    close_conn(conn)
    return templates.TemplateResponse(request=request, name="admin_historico.html", context={
        "usuario_nome": usuario_nome, "usuario_tipo": usuario_tipo, "total_followups": _total_followups_para_template(usuario_id),
        "v": dict(v), "cliente": dict(cli), "historico": hist, "atendimentos": atends
    })


@app.post("/admin/vendedor/{vendedor_id}/historico/{hist_id}/excluir")
def admin_excluir_historico(vendedor_id: int, hist_id: int, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM historico WHERE id = %s AND vendedor_id = %s", (hist_id, vendedor_id))
    conn.commit()
    cur.close()
    close_conn(conn)
    return {"status": "ok"}


@app.post("/admin/vendedor/{vendedor_id}/historico/limpar/{cliente_id}")
def admin_limpar_historico(vendedor_id: int, cliente_id: int, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT whatsapp FROM clientes WHERE id = %s AND vendedor_id = %s", (cliente_id, vendedor_id))
    row = cur.fetchone()
    if row:
        cur.execute("DELETE FROM historico WHERE whatsapp = %s AND vendedor_id = %s", (row[0], vendedor_id))
        conn.commit()
    cur.close()
    close_conn(conn)
    return RedirectResponse(url=f"/admin/vendedor/{vendedor_id}/cliente/{cliente_id}/historico", status_code=303)


@app.post("/admin/vendedor/{vendedor_id}/atendimento/{atend_id}/excluir")
def admin_excluir_atendimento(vendedor_id: int, atend_id: int, usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM atendimentos WHERE id = %s", (atend_id,))
    conn.commit()
    cur.close()
    close_conn(conn)
    return {"status": "ok"}



# ============ PROTEÃ‡ÃƒO IP + WHATSAPP OBRIGATÃ“RIO ============

from fastapi import HTTPException

def obter_ip(request: Request):
    # Render fica atrÃ¡s de proxy: pega o IP real do X-Forwarded-For
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "desconhecido"


def contar_signups_ip(ip, horas=1):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM tentativas_signup
        WHERE ip = %s AND criado_em >= NOW() - INTERVAL '%s hours'
    """, (ip, horas))
    total = cur.fetchone()[0]
    cur.close()
    close_conn(conn)
    return total


def registrar_tentativa_ip(ip):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO tentativas_signup (ip) VALUES (%s)", (ip,))
    conn.commit()
    cur.close()
    close_conn(conn)


def validar_whatsapp(wpp):
    # Remove tudo que nÃ£o for dÃ­gito
    limpo = "".join(filter(str.isdigit, wpp or ""))
    # Aceita 10 ou 11 dÃ­gitos (com ou sem o 9 na frente)
    if len(limpo) not in (10, 11):
        return None, "WhatsApp invÃ¡lido. Digite DDD + nÃºmero (10 ou 11 dÃ­gitos)."
    # Se tiver 13 dÃ­gitos (com 55 do Brasil), remove o 55
    if len(limpo) == 13 and limpo.startswith("55"):
        limpo = limpo[2:]
    if len(limpo) == 12 and limpo.startswith("55"):
        limpo = limpo[2:]
    if len(limpo) not in (10, 11):
        return None, "WhatsApp invÃ¡lido. Digite DDD + nÃºmero (10 ou 11 dÃ­gitos)."
    return limpo, None


def criar_vendedor_v2(nome, email, senha, whatsapp):
    # Valida senha forte
    erro_senha = validar_senha_forte(senha)
    if erro_senha:
        return False, erro_senha, None

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
    if cur.fetchone():
        cur.close()
        close_conn(conn)
        return False, "Email ja cadastrado", None
    cur.execute("SELECT id FROM usuarios WHERE whatsapp = %s", (whatsapp,))
    if cur.fetchone():
        cur.close()
        close_conn(conn)
        return False, "WhatsApp ja cadastrado", None
    h = pwd_context.hash(senha)
    cur.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo, whatsapp) VALUES (%s, %s, %s, 'atendente', %s) RETURNING id",
        (nome, email, h, whatsapp)
    )
    uid = cur.fetchone()[0]
    cur.execute("INSERT INTO vendedores (usuario_id, plano, onboarding_completo) VALUES (%s, 'gratis', FALSE)", (uid,))
    conn.commit()
    cur.close()
    close_conn(conn)
    return True, "OK", uid


# ============ ADMIN â€” CRIAR DADOS PELO VENDEDOR ============

@app.post("/admin/vendedor/{vendedor_id}/nicho/criar")
def admin_criar_nicho(vendedor_id: int, nome: str = Form(...), produto: str = Form(""), publico: str = Form(""), preco: str = Form(""), dor: str = Form(""), objecao: str = Form(""), diferencial: str = Form(""), tom: str = Form(""), usuario_id: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    pg = gerar_prompt_personalizado(nome, produto, publico, preco, dor, objecao, diferencial, tom)
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






# ============ FOLLOW-UPS AUTOMÃTICOS ============

def calcular_followups_auto(vendedor_id):
    """
    Analisa todos os clientes do vendedor e calcula quem precisa de atenÃ§Ã£o.
    Retorna dict com listas: urgente, atencao, agenda.
    """
    from datetime import date, timedelta, datetime as dt

    # Regras: quanto tempo sem contato antes de sugerir follow-up (em dias)
    REGRAS = {
        "novo lead": 1,
        "lead": 1,
        "em atendimento": 2,
        "negociando": 2,
        "negociaÃ§Ã£o": 1,
        "negociacao": 1,
        "cliente": 15,
        "perdido": None,  # nunca
    }

    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT c.id, c.nome, c.whatsapp, c.status, c.origem,
               c.criado_em, c.atualizado_em,
               MAX(h.criado_em) as ultima_msg,
               COUNT(h.id) as total_msgs
        FROM clientes c
        LEFT JOIN historico h ON h.whatsapp = c.whatsapp AND h.vendedor_id = c.vendedor_id
        WHERE c.vendedor_id = %s
        GROUP BY c.id, c.nome, c.whatsapp, c.status, c.origem, c.criado_em, c.atualizado_em
    """, (vendedor_id,))
    clientes = [dict(r) for r in cur.fetchall()]
    cur.close()
    close_conn(conn)

    hoje = date.today()
    urgente = []
    atencao = []
    agenda = []

    for c in clientes:
        s = (c["status"] or "novo lead").lower().strip()
        dias = REGRAS.get(s)
        if dias is None:
            continue  # perdido - nao mostra

        # Referencia: ultima mensagem; se nunca teve, usa criado_em
        ref = c["ultima_msg"]
        if ref is None:
            ref = c["criado_em"]
        if ref is None:
            continue

        # Se for datetime, converte pra date
        if isinstance(ref, dt):
            ref_data = ref.date()
        else:
            ref_data = ref

        proxima = ref_data + timedelta(days=dias)
        dias_diff = (proxima - hoje).days

        item = {
            "id": c["id"],
            "nome": c["nome"],
            "whatsapp": c["whatsapp"],
            "status": s,
            "origem": c["origem"],
            "total_msgs": c["total_msgs"],
            "ultima_msg": ref_data,
            "proxima": proxima,
            "dias_diff": dias_diff,
            "dias_sem_contato": (hoje - ref_data).days,
        }

        if dias_diff < 0:
            # Atrasado
            item["urgencia"] = "urgente"
            urgente.append(item)
        elif dias_diff == 0:
            item["urgencia"] = "hoje"
            urgente.append(item)
        elif dias_diff <= 2:
            item["urgencia"] = "atencao"
            atencao.append(item)
        else:
            item["urgencia"] = "agenda"
            agenda.append(item)

    # Ordena por mais tempo sem contato
    urgente.sort(key=lambda x: x["dias_sem_contato"], reverse=True)
    atencao.sort(key=lambda x: x["dias_sem_contato"], reverse=True)
    agenda.sort(key=lambda x: x["dias_diff"])

    return {
        "urgente": urgente,
        "atencao": atencao,
        "agenda": agenda[:20],
        "total": len(urgente) + len(atencao) + len(agenda),
        "total_urgente": len(urgente),
    }


def texto_sugestao(f):
    """Gera uma sugestÃ£o curta de aÃ§Ã£o baseada no estado."""
    s = f["status"]
    d = f["dias_sem_contato"]
    if s in ["negociaÃ§Ã£o", "negociacao", "negociando"]:
        if d >= 2:
            return f"Cliente em negociaÃ§Ã£o hÃ¡ {d} dias sem contato. Cobrar proposta!"
        return "Cliente em negociaÃ§Ã£o. Vale confirmar interesse hoje."
    if s in ["novo lead", "lead"]:
        if d >= 2:
            return f"Lead novo hÃ¡ {d} dias sem resposta. Reengajar agora."
        return "Lead novo. Fazer primeiro contato hoje."
    if s in ["em atendimento"]:
        if d >= 3:
            return f"Em atendimento hÃ¡ {d} dias parado. Retomar conversa."
        return "Acompanhar atendimento. Ver se tem novidade."
    if s == "cliente":
        if d >= 20:
            return f"Cliente hÃ¡ {d} dias sem contato. PÃ³s-venda pra fortalecer relaÃ§Ã£o."
        return "Cliente ativo. Vale um follow-up de relacionamento."
    return "Entrar em contato."


@app.get("/followups", response_class=HTMLResponse)
def tela_followups(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")

    dados = calcular_followups_auto(v["id"])

    # Adiciona sugestÃ£o de texto em cada item
    for lista in [dados["urgente"], dados["atencao"], dados["agenda"]]:
        for f in lista:
            f["sugestao"] = texto_sugestao(f)

    return templates.TemplateResponse(request=request, name="followups.html", context={
        "usuario_nome": usuario_nome,
        "usuario_tipo": usuario_tipo, "total_followups": _total_followups_para_template(usuario_id),
        "urgente": dados["urgente"],
        "atencao": dados["atencao"],
        "agenda": dados["agenda"],
        "total": dados["total"],
        "total_urgente": dados["total_urgente"],
    })





# ============ CONTADOR DE FOLLOWUPS (para o menu) ============

def _total_followups_para_template(usuario_id):
    """Conta quantos follow-ups pendentes o vendedor tem (pra badge no menu)."""
    if not usuario_id:
        return 0
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, followup_snooze_ate FROM vendedores WHERE usuario_id = %s", (usuario_id,))
        row = cur.fetchone()
        if not row:
            cur.close()
            close_conn(conn)
            return 0
        vid = row[0]
        snooze = row[1] if len(row) > 1 else None
        # Se snooze ainda esta ativo, retorna 0
        if snooze:
            from datetime import datetime as _dt
            try:
                agora = _dt.now(snooze.tzinfo) if snooze.tzinfo else _dt.now()
                if snooze > agora:
                    cur.close()
                    close_conn(conn)
                    return 0
            except Exception:
                pass
        cur.execute("""
            SELECT COUNT(*) FROM clientes c
            WHERE c.vendedor_id = %s
            AND LOWER(COALESCE(c.status, 'novo lead')) NOT IN ('perdido')
        """, (vid,))
        # Conta rapido: usa a mesma logica simplificada (clientes que precisam atencao)
        # Aqui so retorna clientes ativos - o calculo real fica na tela /followups
        cur.execute("""
            SELECT COUNT(*) FROM clientes c
            WHERE c.vendedor_id = %s
            AND LOWER(COALESCE(c.status, 'novo lead')) NOT IN ('perdido')
            AND (
                (LOWER(COALESCE(c.status, '')) IN ('novo lead','lead') AND
                 COALESCE((SELECT MAX(h.criado_em) FROM historico h WHERE h.whatsapp=c.whatsapp AND h.vendedor_id=c.vendedor_id), c.criado_em) < NOW() - INTERVAL '1 day')
                OR
                (LOWER(COALESCE(c.status, '')) IN ('em atendimento','negociando') AND
                 COALESCE((SELECT MAX(h.criado_em) FROM historico h WHERE h.whatsapp=c.whatsapp AND h.vendedor_id=c.vendedor_id), c.criado_em) < NOW() - INTERVAL '2 days')
                OR
                (LOWER(COALESCE(c.status, '')) IN ('negociaÃ§Ã£o','negociacao') AND
                 COALESCE((SELECT MAX(h.criado_em) FROM historico h WHERE h.whatsapp=c.whatsapp AND h.vendedor_id=c.vendedor_id), c.criado_em) < NOW() - INTERVAL '1 day')
                OR
                (LOWER(COALESCE(c.status, '')) = 'cliente' AND
                 COALESCE((SELECT MAX(h.criado_em) FROM historico h WHERE h.whatsapp=c.whatsapp AND h.vendedor_id=c.vendedor_id), c.criado_em) < NOW() - INTERVAL '15 days')
            )
        """, (vid,))
        total = cur.fetchone()[0]
        cur.close()
        close_conn(conn)
        return total
    except Exception as e:
        print(f"Erro contador followups: {e}")
        return 0





# ============ BEM-VINDO ============

@app.get("/bem-vindo", response_class=HTMLResponse)
def tela_bemvindo(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    ns = listar_nichos(v["id"])
    return templates.TemplateResponse(request=request, name="bem_vindo.html", context={
        "usuario_nome": usuario_nome,
        "usuario_tipo": usuario_tipo,
        "total_followups": _total_followups_para_template(usuario_id),
        "primeiro_nicho": dict(ns[0]) if ns else None
    })





# ============ CAPTURA DE LEADS (LANDING) ============

@app.post("/capturar_lead")
def capturar_lead(request: Request, nome: str = Form(...), whatsapp: str = Form(...), email: str = Form("")):
    ip = obter_ip(request)

    wpp_limpo, erro_wpp = validar_whatsapp(whatsapp)
    if erro_wpp:
        return RedirectResponse(url=f"/?erro_lead=WhatsApp+invalido#contato", status_code=303)

    conn = get_conn()
    cur = conn.cursor()
    # Se ja existe esse whatsapp, atualiza o nome/email
    cur.execute("SELECT id FROM leads_landing WHERE whatsapp = %s", (wpp_limpo,))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE leads_landing SET nome=%s, email=%s, ip=%s WHERE id=%s", (nome, email, ip, row[0]))
    else:
        cur.execute("INSERT INTO leads_landing (nome, whatsapp, email, ip) VALUES (%s, %s, %s, %s)",
                    (nome, wpp_limpo, email, ip))
    conn.commit()
    cur.close()
    close_conn(conn)

    return RedirectResponse(url="/?capturado=1#contato", status_code=303)


@app.get("/admin/leads", response_class=HTMLResponse)
def admin_leads(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM leads_landing ORDER BY criado_em DESC")
    leads = [dict(l) for l in cur.fetchall()]
    cur.close()
    close_conn(conn)
    return templates.TemplateResponse(request=request, name="admin_leads.html", context={
        "usuario_nome": usuario_nome,
        "usuario_tipo": usuario_tipo,
        "leads": leads,
        "total_followups": _total_followups_para_template(usuario_id),
    })



# ============ VER LANDING (mesmo logado) ============

@app.get("/ver-landing", response_class=HTMLResponse)
def ver_landing(request: Request):
    return templates.TemplateResponse(request=request, name="landing.html", context={})



# ============ MODO NÃƒO PERTURBE (SNOOZE) ============

@app.post("/snooze-followups")
async def snooze_followups(request: Request, usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    try:
        form = await request.form()
        dias_str = form.get("dias", "1")
        dias = int(str(dias_str).strip())
    except Exception:
        dias = 1
    if dias not in [1, 2, 3, 7]:
        dias = 1
    from datetime import datetime, timedelta
    ate = datetime.now() + timedelta(days=dias)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE vendedores SET followup_snooze_ate = %s WHERE id = %s", (ate, v["id"]))
    conn.commit()
    cur.close()
    close_conn(conn)
    return RedirectResponse(url="/followups", status_code=303)


@app.post("/snooze-followups/cancelar")
def cancelar_snooze(usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE vendedores SET followup_snooze_ate = NULL WHERE id = %s", (v["id"],))
    conn.commit()
    cur.close()
    close_conn(conn)
    return RedirectResponse(url="/clientes", status_code=303)


def request_referer_ou_clientes():
    return "/clientes"


@app.get("/api/snooze-status")
def snooze_status(usuario_id: str = Cookie(None)):
    if not usuario_id:
        return {"ativo": False, "ate": None}
    v = buscar_vendedor(usuario_id)
    if not v:
        return {"ativo": False, "ate": None}
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT followup_snooze_ate FROM vendedores WHERE id = %s", (v["id"],))
    row = cur.fetchone()
    cur.close()
    close_conn(conn)
    ate = row[0] if row else None
    if not ate:
        return {"ativo": False, "ate": None}
    from datetime import datetime as _dt
    agora = _dt.now(ate.tzinfo) if ate.tzinfo else _dt.now()
    if ate > agora:
        return {"ativo": True, "ate": ate.isoformat(), "dias": (ate - agora).days}
    return {"ativo": False, "ate": None}




def validar_texto_minimo(texto, min_chars, campo):
    t = (texto or "").strip()
    if len(t) < min_chars:
        return f"O campo '{campo}' precisa ter pelo menos {min_chars} caracteres."
    return None


def validar_respostas_onboarding(produto, publico, preco, dor, objecao, diferencial, tom):
    campos = [
        ("O que voce vende", produto, 5),
        ("Para quem vende", publico, 5),
        ("Preco", preco, 2),
        ("Dor do cliente", dor, 5),
        ("Objecao", objecao, 5),
        ("Diferencial", diferencial, 5),
        ("Tom de voz", tom, 2),
    ]
    for nome, valor, minimo in campos:
        erro = validar_texto_minimo(valor, minimo, nome)
        if erro:
            return erro
    return None





def validar_nicho_simples(nome, produto):
    """Validacao clara e previsivel. Bloqueia mistura de produtos com mensagem educativa."""
    import re

    nome_limpo = (nome or "").strip().lower()
    produto_limpo = (produto or "").strip().lower()

    # Nome muito curto
    if len(nome_limpo) < 3:
        return False, "O nome do nicho precisa ter pelo menos 3 letras."

    # Palavras vagas
    vagas = ["tudo", "coisas", "produtos", "servicos", "serviÃ§os", "geral", "varios", "varios produtos", "teste", "negocio", "negÃ³cio"]
    if nome_limpo in vagas:
        return False, (
            f"'{nome}' e muito vago. Escolha algo especifico.\n\n"
            "âœ… BOM: 'carro', 'moto', 'curso de ingles', 'pizza', 'consultoria'\n"
            "âŒ RUIM: 'produtos', 'coisas', 'tudo', 'servicos gerais'"
        )

    # Detecta mistura: "X e Y", "X + Y", "X & Y", "X, Y", "X / Y", "X ou Y", "X - Y"
    produtos_comuns = [
        "carro", "carros", "moto", "motos", "caminhao", "caminhÃ£o", "caminhoes",
        "bicicleta", "bicicletas", "barco", "barcos", "aviao", "aviÃ£o",
        "pizza", "hamburguer", "hambÃºrguer", "lanche", "lanches", "sushi",
        "curso", "cursos", "mentoria", "mentorias", "consultoria", "consultorias",
        "treinamento", "treinamentos", "aula", "aulas",
        "seguro", "seguros", "consorcio", "consÃ³rcio", "consorcios",
        "financiamento", "financiamentos", "emprestimo", "emprÃ©stimo",
        "plano", "planos", "servico", "serviÃ§o", "servicos", "serviÃ§os",
        "produto", "produtos", "roupa", "roupas", "sapato", "sapatos",
        "celular", "celulares", "computador", "computadores", "eletronico", "eletrÃ´nico",
        "livro", "livros", "curso online", "software", "app", "aplicativo",
        "terreno", "terrenos", "casa", "casas", "apartamento", "apartamentos",
        "caminha", "caminhas", "moto aquatica", "jet ski", "motoaquatica",
    ]

    # Padroes de separadores
    padroes = [
        r"\b(\w{3,})\s+(?:e|ou)\s+(\w{3,})\b",       # "X e Y", "X ou Y"
        r"\b(\w{3,})\s*[+&]\s*(\w{3,})\b",           # "X + Y", "X & Y"
        r"\b(\w{3,})\s*,\s*(\w{3,})\b",              # "X, Y"
        r"\b(\w{3,})\s*/\s*(\w{3,})\b",              # "X / Y"
    ]

    conectivos_ok = ["para", "com", "sem", "de", "da", "do", "em", "no", "na", "dos", "das"]

    for padrao in padroes:
        for match in re.finditer(padrao, produto_limpo):
            a, b = match.group(1).lower(), match.group(2).lower()
            if a in conectivos_ok or b in conectivos_ok:
                continue
            if a in produtos_comuns and b in produtos_comuns and a != b:
                return False, (
                    f"Voce mencionou 2 produtos diferentes: '{a}' e '{b}'.\n\n"
                    "Cada nicho deve ter apenas UM produto ou servico.\n\n"
                    "âœ… CERTO: criar 2 nichos separados â€” um para carro, outro para moto\n"
                    "âŒ ERRADO: 'vendo carro e moto' no mesmo nicho\n\n"
                    "Dica: se vende os dois, cadastre primeiro 'carro', depois crie outro nicho 'moto'."
                )

    # Detecta virgula multipla tipo "carro, moto, bicicleta"
    if produto_limpo.count(",") >= 1 and len(produtos_comuns) > 0:
        partes = [p.strip() for p in produto_limpo.split(",") if p.strip()]
        hits = [p for p in partes if any(pc in p for pc in produtos_comuns)]
        if len(hits) >= 2:
            return False, (
                f"Voce listou varios produtos separados por virgula: {', '.join(hits[:3])}.\n\n"
                "Cada nicho deve ter apenas UM produto ou servico.\n\n"
                "âœ… CERTO: criar um nicho para cada produto\n"
                "âŒ ERRADO: 'carro, moto, bicicleta' tudo junto"
            )

    return True, ""



# ============ EDITAR NICHO (campos permitidos) ============

@app.post("/nicho/{nicho_id}/editar")
def editar_nicho(nicho_id: int, publico: str = Form(...), preco: str = Form(...), dor: str = Form(...), objecao: str = Form(...), diferencial: str = Form(...), tom: str = Form(...), usuario_id: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")

    n = buscar_nicho(nicho_id)
    if not n or n["vendedor_id"] != v["id"]:
        return RedirectResponse(url="/meus_nichos?erro=Nicho+nao+encontrado", status_code=303)

    # Valida as respostas
    erro = validar_respostas_onboarding(n["produto"] or "", publico, preco, dor, objecao, diferencial, tom)
    if erro:
        from urllib.parse import quote
        return RedirectResponse(url=f"/meus_nichos?erro={quote(erro)}", status_code=303)

    # Regera o prompt com os novos dados (mantendo nome e produto originais)
    pg = gerar_prompt_personalizado(n["nome"], n["produto"] or "", publico, preco, dor, objecao, diferencial, tom)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE nichos SET publico=%s, preco=%s, dor=%s, objecao=%s, diferencial=%s, tom=%s, prompt_gerado=%s
        WHERE id = %s AND vendedor_id = %s
    """, (publico, preco, dor, objecao, diferencial, tom, pg, nicho_id, v["id"]))
    conn.commit()
    cur.close()
    close_conn(conn)

    return RedirectResponse(url="/meus_nichos?ok=1", status_code=303)



# ============ ADMIN â€” DASHBOARD COM GRÃFICO ============

@app.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id or usuario_tipo != "admin":
        return RedirectResponse(url="/login")

    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Total de vendedores
    cur.execute("SELECT COUNT(*) as t FROM vendedores")
    total_vend = cur.fetchone()["t"]

    # Total de leads capturados
    cur.execute("SELECT COUNT(*) as t FROM leads_landing")
    total_leads = cur.fetchone()["t"]

    # Total de clientes (todos os vendedores)
    cur.execute("SELECT COUNT(*) as t FROM clientes")
    total_clientes = cur.fetchone()["t"]

    # Total de atendimentos
    cur.execute("SELECT COUNT(*) as t FROM atendimentos")
    total_atend = cur.fetchone()["t"]

    # Vendedores por mÃªs (Ãºltimos 6 meses)
    cur.execute("""
        SELECT TO_CHAR(criado_em, 'YYYY-MM') as mes, COUNT(*) as qtd
        FROM vendedores
        WHERE criado_em >= NOW() - INTERVAL '6 months'
        GROUP BY mes ORDER BY mes
    """)
    vend_mes_raw = {r["mes"]: r["qtd"] for r in cur.fetchall()}

    # Leads por mÃªs (Ãºltimos 6 meses)
    cur.execute("""
        SELECT TO_CHAR(criado_em, 'YYYY-MM') as mes, COUNT(*) as qtd
        FROM leads_landing
        WHERE criado_em >= NOW() - INTERVAL '6 months'
        GROUP BY mes ORDER BY mes
    """)
    leads_mes_raw = {r["mes"]: r["qtd"] for r in cur.fetchall()}

    # Monta os Ãºltimos 6 meses (mesmo os zerados)
    from datetime import date
    hoje = date.today()
    meses = []
    for i in range(5, -1, -1):
        # Calcula o mÃªs retroativo
        ano = hoje.year
        mes = hoje.month - i
        while mes <= 0:
            mes += 12
            ano -= 1
        chave = f"{ano:04d}-{mes:02d}"
        nome_mes = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"][mes - 1]
        meses.append({
            "chave": chave,
            "nome": nome_mes,
            "ano": ano,
            "vendedores": vend_mes_raw.get(chave, 0),
            "leads": leads_mes_raw.get(chave, 0),
        })

    max_vend = max([m["vendedores"] for m in meses] + [1])
    max_leads = max([m["leads"] for m in meses] + [1])

    # Crescimento vs mÃªs anterior
    if len(meses) >= 2:
        atual = meses[-1]["vendedores"]
        anterior = meses[-2]["vendedores"]
        if anterior > 0:
            cresc = round(((atual - anterior) / anterior) * 100, 1)
        elif atual > 0:
            cresc = 100
        else:
            cresc = 0
    else:
        cresc = 0

    # Plano atual de cada vendedor
    cur.execute("""
        SELECT plano, COUNT(*) as qtd FROM vendedores GROUP BY plano
    """)
    por_plano = {r["plano"]: r["qtd"] for r in cur.fetchall()}

    cur.close()
    close_conn(conn)

    return templates.TemplateResponse(request=request, name="admin_dashboard.html", context={
        "usuario_nome": usuario_nome,
        "usuario_tipo": usuario_tipo,
        "total_followups": _total_followups_para_template(usuario_id),
        "total_vend": total_vend,
        "total_leads": total_leads,
        "total_clientes": total_clientes,
        "total_atend": total_atend,
        "meses": meses,
        "max_vend": max_vend,
        "max_leads": max_leads,
        "crescimento": cresc,
        "por_plano": por_plano,
    })


def migrar_historico_antigo():
    """Migra historico salvo com usuario_id para vendedor_id correto."""
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # Busca todos os mapeamentos usuario_id -> vendedor_id
        cur.execute("SELECT usuario_id, id FROM vendedores")
        mapa = {r["usuario_id"]: r["id"] for r in cur.fetchall()}
        # Atualiza historico onde vendedor_id Ã© um usuario_id vÃ¡lido
        total = 0
        for uid, vid in mapa.items():
            if uid == vid:
                continue
            cur.execute("UPDATE historico SET vendedor_id = %s WHERE vendedor_id = %s", (vid, uid))
            total += cur.rowcount
        conn.commit()
        cur.close()
        close_conn(conn)
        print(f"Historico migrado: {total} registros atualizados")
    except Exception as e:
        print(f"Erro migrar historico: {e}")



# ============ PWA ============

from fastapi.responses import FileResponse

@app.get("/manifest.json", include_in_schema=False)
def manifest():
    return FileResponse("static/manifest.json", media_type="application/manifest+json")


@app.get("/service-worker.js", include_in_schema=False)
def service_worker():
    return FileResponse("static/service-worker.js", media_type="application/javascript")


# ============ CONFIGURACOES ============

@app.get("/configuracoes", response_class=HTMLResponse)
def tela_configuracoes(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT followup_snooze_ate FROM vendedores WHERE id = %s", (v["id"],))
    row = cur.fetchone()
    cur.close()
    close_conn(conn)

    snooze_ate = row[0] if row else None
    snooze_ativo = False
    snooze_data = None
    snooze_dias = 0
    if snooze_ate:
        from datetime import datetime as _dt
        agora = _dt.now(snooze_ate.tzinfo) if snooze_ate.tzinfo else _dt.now()
        if snooze_ate > agora:
            snooze_ativo = True
            snooze_data = snooze_ate.strftime("%d/%m/%Y")
            snooze_dias = (snooze_ate - agora).days

    return templates.TemplateResponse(request=request, name="configuracoes.html", context={
        "usuario_nome": usuario_nome,
        "usuario_tipo": usuario_tipo,
        "total_followups": _total_followups_para_template(usuario_id),
        "snooze_ativo": snooze_ativo,
        "snooze_data": snooze_data,
        "snooze_dias": snooze_dias,
    })



# ============ SISTEMA DE INDICACAO ============

import secrets
import string

def gerar_codigo_indicacao():
    """Gera codigo unico de 6 caracteres alfanumericos."""
    alfabeto = string.ascii_uppercase + string.digits
    for _ in range(20):
        codigo = ''.join(secrets.choice(alfabeto) for _ in range(6))
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id FROM vendedores WHERE codigo_indicacao = %s", (codigo,))
        if not cur.fetchone():
            cur.close()
            close_conn(conn)
            return codigo
        cur.close()
        close_conn(conn)
    return None


def garantir_codigo_vendedor(vendedor_id):
    """Garante que o vendedor tem um codigo. Cria se nao tiver."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT codigo_indicacao FROM vendedores WHERE id = %s", (vendedor_id,))
    row = cur.fetchone()
    if row and row[0]:
        cur.close()
        close_conn(conn)
        return row[0]
    codigo = gerar_codigo_indicacao()
    cur.execute("UPDATE vendedores SET codigo_indicacao = %s WHERE id = %s", (codigo, vendedor_id))
    conn.commit()
    cur.close()
    close_conn(conn)
    return codigo


def registrar_indicacao(codigo_ref, indicado_id):
    """Registra que indicado_id foi indicado por quem tem codigo_ref."""
    if not codigo_ref:
        return False
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id FROM vendedores WHERE codigo_indicacao = %s", (codigo_ref.strip().upper(),))
    indicador = cur.fetchone()
    if not indicador:
        cur.close()
        close_conn(conn)
        return False
    indicador_id = indicador["id"]
    if indicador_id == indicado_id:
        cur.close()
        close_conn(conn)
        return False
    cur.execute("UPDATE vendedores SET indicado_por = %s WHERE id = %s", (indicador_id, indicado_id))
    cur.execute("INSERT INTO indicacoes (indicador_id, indicado_id, codigo) VALUES (%s, %s, %s)",
                (indicador_id, indicado_id, codigo_ref.strip().upper()))
    conn.commit()
    cur.close()
    close_conn(conn)
    return True


def recompensar_indicador(indicado_id):
    """Quando o indicado paga o 1o PIX, da +30 dias pro indicador."""
    from datetime import datetime, timedelta
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    # Pega indicacao pendente
    cur.execute("""SELECT i.id, i.indicador_id FROM indicacoes i
                   WHERE i.indicado_id = %s AND i.recompensado = FALSE LIMIT 1""", (indicado_id,))
    ind = cur.fetchone()
    if not ind:
        cur.close()
        close_conn(conn)
        return False
    # Pega dados do indicador
    cur.execute("SELECT plano, plano_expira_em, usuario_id FROM vendedores WHERE id = %s", (ind["indicador_id"],))
    v = cur.fetchone()
    if not v:
        cur.close()
        close_conn(conn)
        return False
    # Calcula nova expiracao
    agora = datetime.now()
    base = v["plano_expira_em"] if v["plano_expira_em"] and v["plano_expira_em"] > agora else agora
    nova_exp = base + timedelta(days=30)
    # Se for gratis, promove pra basico por 30 dias (recompensa)
    if v["plano"] == "gratis":
        cur.execute("UPDATE vendedores SET plano = 'basico', plano_expira_em = %s WHERE id = %s", (nova_exp, ind["indicador_id"]))
    else:
        cur.execute("UPDATE vendedores SET plano_expira_em = %s WHERE id = %s", (nova_exp, ind["indicador_id"]))
    # Marca recompensado
    cur.execute("UPDATE indicacoes SET recompensado = TRUE, recompensado_em = CURRENT_TIMESTAMP WHERE id = %s", (ind["id"],))
    conn.commit()
    cur.close()
    close_conn(conn)
    return True


def estatisticas_indicacao(vendedor_id):
    """Retorna estatisticas do vendedor indicador."""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT COUNT(*) as t FROM indicacoes WHERE indicador_id = %s", (vendedor_id,))
    total = cur.fetchone()["t"]
    cur.execute("SELECT COUNT(*) as t FROM indicacoes WHERE indicador_id = %s AND recompensado = TRUE", (vendedor_id,))
    pagos = cur.fetchone()["t"]
    # Lista de indicados
    cur.execute("""SELECT i.criado_em, i.recompensado, u.nome, u.email
                   FROM indicacoes i
                   JOIN vendedores v ON v.id = i.indicado_id
                   JOIN usuarios u ON u.id = v.usuario_id
                   WHERE i.indicador_id = %s
                   ORDER BY i.criado_em DESC LIMIT 20""", (vendedor_id,))
    lista = [dict(r) for r in cur.fetchall()]
    cur.close()
    close_conn(conn)
    return {"total": total, "pagos": pagos, "dias_ganhos": pagos * 30, "lista": lista}


# ============ ROTA /INDICAR ============

@app.get("/indicar", response_class=HTMLResponse)
def tela_indicar(request: Request, usuario_id: str = Cookie(None), usuario_nome: str = Cookie(None), usuario_tipo: str = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/login")
    v = buscar_vendedor(usuario_id)
    if not v:
        return RedirectResponse(url="/onboarding")
    codigo = garantir_codigo_vendedor(v["id"])
    stats = estatisticas_indicacao(v["id"])
    return templates.TemplateResponse(request=request, name="indicar.html", context={
        "usuario_nome": usuario_nome,
        "usuario_tipo": usuario_tipo,
        "total_followups": _total_followups_para_template(usuario_id),
        "codigo": codigo,
        "stats": stats,
    })





# ============ BACKUP AUTOMATICO ============

@app.get("/admin/backup")
def admin_backup(token: str = ""):
    """Faz dump completo do banco. Protegido por token na query."""
    import os as _os
    from fastapi.responses import JSONResponse
    from datetime import datetime as _dt

    # Token secreto â€” pode definir BACKUP_TOKEN no Render
    token_esperado = _os.getenv("BACKUP_TOKEN", "")
    if not token_esperado or token != token_esperado:
        return JSONResponse({"erro": "token invalido"}, status_code=403)

    tabelas = [
        "usuarios", "vendedores", "nichos", "clientes",
        "historico", "atendimentos", "pagamentos",
        "tentativas_signup", "leads_landing", "indicacoes"
    ]

    dump = {
        "gerado_em": _dt.now().isoformat(),
        "tabelas": {}
    }

    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    for tabela in tabelas:
        try:
            cur.execute(f"SELECT * FROM {tabela}")
            linhas = []
            for r in cur.fetchall():
                # Converte datetime pra string
                linha = {}
                for k, v in dict(r).items():
                    if hasattr(v, "isoformat"):
                        linha[k] = v.isoformat()
                    else:
                        linha[k] = v
                linhas.append(linha)
            dump["tabelas"][tabela] = linhas
        except Exception as e:
            dump["tabelas"][tabela] = {"erro": str(e)}

    cur.close()
    close_conn(conn)

    return JSONResponse(dump)



# ============ API â€” TOTAL DE FOLLOWUPS ============

@app.get("/api/total-followups")
def api_total_followups(usuario_id: str = Cookie(None)):
    if not usuario_id:
        return {"total": 0}
    try:
        total = _total_followups_para_template(usuario_id)
        return {"total": total}
    except Exception:
        return {"total": 0}



# ============ SEGURANCA ============

def validar_senha_forte(senha):
    """Valida se a senha e forte o suficiente."""
    if not senha or len(senha) < 8:
        return "A senha precisa ter pelo menos 8 caracteres."
    tem_letra = any(c.isalpha() for c in senha)
    tem_numero = any(c.isdigit() for c in senha)
    if not tem_letra or not tem_numero:
        return "A senha precisa ter letras E numeros."
    return None


def contar_tentativas_login(email, ip, minutos=15):
    """Conta tentativas falhas nos ultimos X minutos."""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT COUNT(*) FROM tentativas_login
            WHERE (email = %s OR ip = %s)
              AND sucesso = FALSE
              AND criado_em >= NOW() - INTERVAL '%s minutes'
        """, (email, ip, minutos))
        total = cur.fetchone()[0]
    except Exception:
        total = 0
    cur.close()
    close_conn(conn)
    return total


def registrar_tentativa_login(email, ip, sucesso):
    """Registra uma tentativa de login."""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO tentativas_login (email, ip, sucesso) VALUES (%s, %s, %s)",
                    (email, ip, sucesso))
        conn.commit()
    except Exception:
        pass
    cur.close()
    close_conn(conn)


def limpar_tentativas_antigas():
    """Limpa tentativas mais antigas que 30 dias."""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM tentativas_login WHERE criado_em < NOW() - INTERVAL '30 days'")
        conn.commit()
    except Exception:
        pass
    cur.close()
    close_conn(conn)




# ============ API â€” AVISO DE PLANO ============

@app.get("/api/aviso-plano")
def api_aviso_plano(usuario_id: str = Cookie(None)):
    if not usuario_id:
        return {"mostrar": False}
    try:
        v = buscar_vendedor(usuario_id)
        if not v:
            return {"mostrar": False}
        # So mostra pra planos pagos com expiracao
        if v["plano"] == "gratis" or not v["plano_expira_em"]:
            return {"mostrar": False}

        from datetime import datetime as _dt
        exp = v["plano_expira_em"]
        agora = _dt.now(exp.tzinfo) if exp.tzinfo else _dt.now()
        dias = (exp - agora).days

        # So mostra se faltar 5 dias ou menos E ainda nao expirou
        if dias < 0 or dias > 5:
            return {"mostrar": False}

        return {
            "mostrar": True,
            "dias": dias,
            "plano": v["plano"].upper(),
            "data": exp.strftime("%d/%m/%Y"),
        }
    except Exception as e:
        print(f"Erro aviso plano: {e}")
        return {"mostrar": False}



# ============ DESBLOQUEAR LOGIN (rota secreta) ============

@app.post("/admin/desbloquear")
def desbloquear_login(token: str = "", email: str = ""):
    import os as _os
    from fastapi.responses import JSONResponse
    token_esperado = _os.getenv("BACKUP_TOKEN", "")
    if not token_esperado or token != token_esperado:
        return JSONResponse({"erro": "token invalido"}, status_code=403)

    conn = get_conn()
    cur = conn.cursor()
    if email:
        cur.execute("DELETE FROM tentativas_login WHERE sucesso = FALSE AND email = %s", (email,))
        removidas = cur.rowcount
    else:
        cur.execute("DELETE FROM tentativas_login WHERE sucesso = FALSE")
        removidas = cur.rowcount
    conn.commit()
    cur.close()
    close_conn(conn)
    return {"ok": True, "removidas": removidas}



# ============ API HISTORICO DO CLIENTE ============

@app.get("/api/cliente/{cliente_id}/historico")
def api_historico_cliente(cliente_id: int, usuario_id: str = Cookie(None)):
    if not usuario_id:
        return {"historico": []}
    try:
        v = buscar_vendedor(usuario_id)
        if not v:
            return {"historico": []}
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT whatsapp FROM clientes WHERE id = %s AND vendedor_id = %s", (cliente_id, v["id"]))
        row = cur.fetchone()
        if not row:
            cur.close()
            close_conn(conn)
            return {"historico": []}
        wpp = row["whatsapp"]
        cur.execute("""SELECT direcao, mensagem, criado_em FROM historico
                       WHERE whatsapp = %s AND vendedor_id = %s
                       ORDER BY id DESC LIMIT 20""", (wpp, v["id"]))
        linhas = list(reversed(cur.fetchall()))
        cur.close()
        close_conn(conn)
        return {"historico": [
            {
                "direcao": r["direcao"],
                "mensagem": r["mensagem"][:500],
                "data": r["criado_em"].strftime("%d/%m %H:%M") if r["criado_em"] else ""
            } for r in linhas
        ]}
    except Exception as e:
        print(f"Erro api historico: {e}")
        return {"historico": []}



# ============ API AVISO PLANO BADGE ============

@app.get("/api/aviso-plano-badge")
def api_aviso_plano_badge(usuario_id: str = Cookie(None)):
    if not usuario_id:
        return {"mostrar": False}
    try:
        v = buscar_vendedor(usuario_id)
        if not v:
            return {"mostrar": False}
        if v["plano"] == "gratis" or not v["plano_expira_em"]:
            return {"mostrar": False}
        from datetime import datetime as _dt
        exp = v["plano_expira_em"]
        agora = _dt.now(exp.tzinfo) if exp.tzinfo else _dt.now()
        dias = (exp - agora).days
        if 0 <= dias <= 5:
            return {"mostrar": True, "dias": dias}
        return {"mostrar": False}
    except Exception:
        return {"mostrar": False}



# ============ API FOLLOWUPS RAPIDOS ============

@app.get("/api/followups-rapidos")
def api_followups_rapidos(usuario_id: str = Cookie(None)):
    if not usuario_id:
        return {"itens": []}
    try:
        v = buscar_vendedor(usuario_id)
        if not v:
            return {"itens": []}
        dados = calcular_followups_auto(v["id"])
        itens = []
        for f in dados.get("urgente", [])[:8]:
            itens.append({"id": f["id"], "nome": f["nome"], "whatsapp": f["whatsapp"], "dias_sem_contato": f["dias_sem_contato"], "urgencia": "urgente"})
        for f in dados.get("atencao", [])[:5]:
            itens.append({"id": f["id"], "nome": f["nome"], "whatsapp": f["whatsapp"], "dias_sem_contato": f["dias_sem_contato"], "urgencia": "atencao"})
        return {"itens": itens}
    except Exception as e:
        print(f"Erro api followups rapidos: {e}")
        return {"itens": []}



# ============ STREAMING DE RESPOSTA IA ============

from fastapi.responses import StreamingResponse
import json as _json

@app.get("/api/gerar_stream/{atendimento_id}")
def gerar_stream(atendimento_id: int, usuario_id: str = Cookie(None)):
    import time as _t
    if not usuario_id:
        return StreamingResponse(iter(["data: " + _json.dumps({"tipo": "erro", "msg": "nao logado"}) + chr(10) + chr(10)]), media_type="text/event-stream")

    def evento(tipo, dados):
        return "data: " + _json.dumps({"tipo": tipo, **dados}) + chr(10) + chr(10)

    def stream():
        try:
            yield evento("inicio", {"msg": "aguardando"})
            for _ in range(60):
                conn = get_conn()
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute("SELECT * FROM atendimentos WHERE id = %s AND atendente_id = %s", (atendimento_id, int(usuario_id)))
                a = cur.fetchone()
                cur.close()
                close_conn(conn)
                if not a:
                    yield evento("erro", {"msg": "nao encontrado"})
                    return
                if a.get("status") == "pronto":
                    yield evento("fim", {
                        "o_que_falar": a.get("o_que_falar") or "",
                        "texto_para_enviar": a.get("texto_para_enviar") or "",
                        "estagio": a.get("acao_crm") or "Em Atendimento",
                        "linha_crm": a.get("linha_crm_gerada") or ""
                    })
                    return
                if a.get("status") == "erro":
                    yield evento("erro", {"msg": a.get("o_que_falar") or "Erro na IA"})
                    return
                _t.sleep(0.5)
            yield evento("erro", {"msg": "tempo esgotado"})
        except Exception as e:
            yield evento("erro", {"msg": str(e)})

    return StreamingResponse(stream(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
        "Connection": "keep-alive"
    })


