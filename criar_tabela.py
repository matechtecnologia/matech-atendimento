from app import get_conn

conn = get_conn()
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS tentativas_signup (
        id SERIAL PRIMARY KEY,
        ip TEXT NOT NULL,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_tentativas_ip ON tentativas_signup(ip, criado_em)")
conn.commit()
print("OK: tabela tentativas_signup criada")

cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='tentativas_signup'")
print("Colunas:", [r[0] for r in cur.fetchall()])

cur.close()
conn.close()