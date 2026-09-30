import io

with io.open('app.py', 'r', encoding='utf-8') as f:
    c = f.read()

# Verifica se já tem a criação no inicializar_banco
if 'CREATE TABLE IF NOT EXISTS tentativas_login' in c and 'def inicializar_banco' in c:
    # Já pode ter, mas verifica se tá DENTRO do inicializar_banco
    idx_init = c.find('def inicializar_banco')
    idx_fim_init = c.find('try:\n    inicializar_banco', idx_init)
    trecho_init = c[idx_init:idx_fim_init] if idx_fim_init > 0 else c[idx_init:idx_init+5000]
    
    if 'CREATE TABLE IF NOT EXISTS tentativas_login' in trecho_init:
        print("JA TEM no inicializar_banco")
        exit()

# Adiciona a criação no inicializar_banco
marcador = 'cur.execute("CREATE INDEX IF NOT EXISTS idx_clientes_vendedor'
bloco = '''cur.execute("""CREATE TABLE IF NOT EXISTS tentativas_login (
        id SERIAL PRIMARY KEY,
        email TEXT NOT NULL,
        ip TEXT,
        sucesso BOOLEAN DEFAULT FALSE,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("CREATE INDEX IF NOT EXISTS idx_tentativas_login ON tentativas_login(email, criado_em DESC)")

    '''
if marcador in c:
    c = c.replace(marcador, bloco + marcador, 1)
    print("OK: tabela tentativas_login adicionada no inicializar_banco")
else:
    print("ERRO: marcador nao encontrado")

with io.open('app.py', 'w', encoding='utf-8') as f:
    f.write(c)

print("Pronto")