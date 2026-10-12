import app
c = app.get_conn()
cur = c.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS primeira_cobranca (
    id SERIAL PRIMARY KEY,
    vendedor_id INTEGER NOT NULL,
    plano TEXT NOT NULL,
    data_primeira TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    valor_cobrado NUMERIC DEFAULT 0,
    UNIQUE (vendedor_id)
)
""")
c.commit()
print("OK - tabela primeira_cobranca")
cur.close()
app.close_conn(c)
