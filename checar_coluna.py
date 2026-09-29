from app import get_conn

conn = get_conn()
cur = conn.cursor()
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='usuarios'")
colunas = [r[0] for r in cur.fetchall()]
print("Colunas da tabela usuarios:", colunas)

if "whatsapp" not in colunas:
    print(">>> Coluna whatsapp NAO existe. Criando agora...")
    cur.execute("ALTER TABLE usuarios ADD COLUMN whatsapp TEXT")
    conn.commit()
    print(">>> Coluna whatsapp criada com sucesso!")
else:
    print(">>> Coluna whatsapp JA existe")

cur.close()
conn.close()
print("Fim")