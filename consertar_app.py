import io

path = 'app.py'
with io.open(path, 'r', encoding='utf-8') as f:
    c = f.read()

antigo = """    cur.execute(\"\"\"
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name='usuarios' AND column_name='whatsapp') THEN
                ALTER TABLE usuarios ADD COLUMN whatsapp TEXT;
            END IF;
        END $$;
    \"\"\")"""

novo = """    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='usuarios'")
    cols = [r[0] for r in cur.fetchall()]
    if 'whatsapp' not in cols:
        cur.execute('ALTER TABLE usuarios ADD COLUMN whatsapp TEXT')"""

if antigo in c:
    c = c.replace(antigo, novo)
    with io.open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print("OK: bloco substituido")
else:
    print("AVISO: bloco antigo nao encontrado no app.py")
    print("Talvez nao tenha sido colado. Voce pode ignorar - a coluna ja existe no banco.")