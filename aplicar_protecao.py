import io

path = 'app.py'
with io.open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Tabela tentativas_signup
if 'tentativas_signup' not in c:
    marcador = 'cur.execute("CREATE INDEX IF NOT EXISTS idx_clientes_vendedor'
    bloco_tabela = '''cur.execute("""CREATE TABLE IF NOT EXISTS tentativas_signup (
        id SERIAL PRIMARY KEY,
        ip TEXT NOT NULL,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("CREATE INDEX IF NOT EXISTS idx_tentativas_ip ON tentativas_signup(ip, criado_em)")

    cur.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name='usuarios' AND column_name='whatsapp') THEN
                ALTER TABLE usuarios ADD COLUMN whatsapp TEXT;
            END IF;
        END $$;
    """)

    '''
    if marcador in c:
        c = c.replace(marcador, bloco_tabela + marcador, 1)
        print('OK: tabela tentativas_signup adicionada')
    else:
        print('ERRO: marcador idx_clientes_vendedor nao encontrado')
else:
    print('JA TEM: tabela')

# 2. Funcoes no final
if 'def obter_ip' not in c:
    funcs = '''


# ============ PROTECAO IP + WHATSAPP OBRIGATORIO ============

def obter_ip(request: Request):
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "desconhecido"


def contar_signups_ip(ip, horas=1):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tentativas_signup WHERE ip = %s AND criado_em >= NOW() - INTERVAL '%s hours'", (ip, horas))
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
    limpo = "".join(filter(str.isdigit, wpp or ""))
    if len(limpo) == 13 and limpo.startswith("55"):
        limpo = limpo[2:]
    if len(limpo) == 12 and limpo.startswith("55"):
        limpo = limpo[2:]
    if len(limpo) not in (10, 11):
        return None, "WhatsApp invalido. Digite DDD + numero (10 ou 11 digitos)."
    return limpo, None


def criar_vendedor_v2(nome, email, senha, whatsapp):
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
    cur.execute("INSERT INTO usuarios (nome, email, senha, tipo, whatsapp) VALUES (%s, %s, %s, 'atendente', %s) RETURNING id", (nome, email, h, whatsapp))
    uid = cur.fetchone()[0]
    cur.execute("INSERT INTO vendedores (usuario_id, plano, onboarding_completo) VALUES (%s, 'gratis', FALSE)", (uid,))
    conn.commit()
    cur.close()
    close_conn(conn)
    return True, "OK", uid
'''
    c = c + funcs
    print('OK: funcoes adicionadas')
else:
    print('JA TEM: funcoes')

# 3. Troca rota signup
antigo = '''@app.post("/signup")
def fazer_signup(nome: str = Form(...), email: str = Form(...), senha: str = Form(...)):
    ok, msg = criar_vendedor(nome, email, senha)
    if not ok:
        return RedirectResponse(url=f"/signup?erro={msg}", status_code=303)
    return RedirectResponse(url="/login", status_code=303)'''

novo = '''@app.post("/signup")
def fazer_signup(request: Request, nome: str = Form(...), email: str = Form(...), senha: str = Form(...), whatsapp: str = Form(...)):
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
    return RedirectResponse(url="/login?criado=1", status_code=303)'''

if antigo in c:
    c = c.replace(antigo, novo)
    print('OK: rota signup trocada')
elif 'def fazer_signup(request' in c:
    print('JA TEM: signup novo')
else:
    print('ERRO: rota signup antiga nao encontrada')

with io.open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print('Arquivo app.py salvo')