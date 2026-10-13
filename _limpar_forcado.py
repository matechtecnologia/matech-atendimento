with open("templates/resultado.html", "r", encoding="utf-8") as f:
    linhas = f.readlines()

novas = []
pular = False
for i, l in enumerate(linhas):
    # Se achou FORCAR/FORCA, comeca a pular ate fechar </style>
    if "FORCA" in l and "/*" in l:
        pular = True
        continue
    if pular and "</style>" in l:
        pular = False
        continue
    if pular:
        continue
    novas.append(l)

with open("templates/resultado.html", "w", encoding="utf-8") as f:
    f.writelines(novas)
print("OK - CSS forcado removido do resultado.html")
