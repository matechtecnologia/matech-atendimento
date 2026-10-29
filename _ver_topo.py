with open("plano_ui.py", "r", encoding="utf-8") as f:
    c = f.read()

# Ver o menu atual (linha 77)
inicio = c.find('def _topo(ativo):')
if inicio == -1:
    print("ERRO - nao achei _topo")
else:
    # Mostra as proximas 40 linhas
    pedaco = c[inicio:inicio+2000]
    print(pedaco[:2000])
