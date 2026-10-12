with open("app.py", "r", encoding="utf-8") as f:
    c = f.read()

# 1. Adiciona ?lead=1 no redirect do signup
antigo = '''    return RedirectResponse(url="/login?criado=1", status_code=303)'''
novo = '''    return RedirectResponse(url="/login?criado=1&lead=1", status_code=303)'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - redirect com lead=1")
else:
    print("AVISO - nao achei o redirect")
