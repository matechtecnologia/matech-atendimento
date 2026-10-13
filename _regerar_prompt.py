import app
from gemini import gerar_prompt_personalizado

c = app.get_conn()
cur = c.cursor()
cur.execute("SELECT nome, produto, publico, preco, dor, objecao, diferencial, tom FROM nichos WHERE id = 14")
r = cur.fetchone()

if r:
    prompt_novo = gerar_prompt_personalizado(
        nome_nicho=r[0], produto=r[1], publico=r[2], preco=r[3],
        dor=r[4], objecao=r[5], diferencial=r[6], tom=r[7]
    )
    cur.execute("UPDATE nichos SET prompt_gerado = %s WHERE id = 14", (prompt_novo,))
    c.commit()
    print("OK - prompt regenerado")
    print()
    print("=== PROMPT NOVO (primeiras 500 chars) ===")
    print(prompt_novo[:500])
else:
    print("Nicho 14 nao encontrado")

cur.close()
app.close_conn(c)
