import app
c = app.get_conn()
cur = c.cursor()

for t in ['gestao_empresas', 'gestao_modulos', 'custos_mensais']:
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name=%s 
        ORDER BY ordinal_position
    """, (t,))
    cols = cur.fetchall()
    print(f"\n--- {t} ---")
    if cols:
        for col, tipo in cols:
            print(f"  {col} ({tipo})")
    else:
        print("  (tabela nao existe)")

cur.close()
app.close_conn(c)
