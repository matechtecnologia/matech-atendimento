import app
c = app.get_conn()
cur = c.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS gestao_empresas (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    cnpj TEXT,
    responsavel TEXT,
    whatsapp TEXT,
    email TEXT,
    segmento TEXT,
    status TEXT DEFAULT 'ativa',
    modulos_ativos TEXT,
    receita_mensal NUMERIC DEFAULT 0,
    observacao TEXT,
    criado_em TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS gestao_modulos (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER REFERENCES gestao_empresas(id) ON DELETE CASCADE,
    modulo TEXT NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    valor_mensal NUMERIC DEFAULT 0,
    criado_em TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
)
""")

c.commit()
print("Tabelas criadas")
cur.close()
app.close_conn(c)
