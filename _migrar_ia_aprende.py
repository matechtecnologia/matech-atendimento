import app
c = app.get_conn()
cur = c.cursor()

# 1. Colunas no vendedores
cur.execute("ALTER TABLE vendedores ADD COLUMN IF NOT EXISTS ia_aprende_ativo BOOLEAN DEFAULT FALSE")
cur.execute("ALTER TABLE vendedores ADD COLUMN IF NOT EXISTS analises_acumuladas INTEGER DEFAULT 0")

# 2. Tabela de análises
cur.execute("""
CREATE TABLE IF NOT EXISTS analises_ia (
    id SERIAL PRIMARY KEY,
    atendimento_id INTEGER,
    vendedor_id INTEGER NOT NULL,
    resposta_analisada TEXT,
    inventou BOOLEAN DEFAULT FALSE,
    campo_faltante TEXT,
    o_que_a_ia_disse TEXT,
    pergunta_pro_vendedor TEXT,
    corrigido BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
)
""")

# 3. Tabela de campos extras do nicho
cur.execute("""
CREATE TABLE IF NOT EXISTS nicho_campos_extras (
    id SERIAL PRIMARY KEY,
    nicho_id INTEGER NOT NULL,
    campo TEXT NOT NULL,
    valor TEXT,
    criado_em TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (nicho_id, campo)
)
""")

c.commit()
print("OK - colunas e tabelas criadas")

cur.close()
app.close_conn(c)
