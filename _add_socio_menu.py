with open("plano_ui.py", "r", encoding="utf-8") as f:
    c = f.read()

# Adiciona o item "Socio" no menu (dentro do _topo)
antigo = '''        ("/plano/diario", "Diario", "diario"),
    ]'''

novo = '''        ("/plano/diario", "Diario", "diario"),
        ("/plano/socio", "Socio", "socio"),
    ]'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    with open("plano_ui.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - Socio adicionado no menu")
else:
    print("AVISO - nao achei o menu")
