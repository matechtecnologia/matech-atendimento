import os

pasta = "templates"
link = '<a href="https://wa.me/5512997291583?text=Oi%2C%20preciso%20de%20ajuda%20com%20o%20M.A%20Tech" target="_blank" rel="noopener">Suporte</a>\n'

arquivos = [f for f in os.listdir(pasta) if f.endswith(".html")]

for arq in arquivos:
    caminho = os.path.join(pasta, arq)
    with open(caminho, "r", encoding="utf-8") as f:
        conteudo = f.read()

    if "wa.me/5512997291583" in conteudo:
        print(f"Pulado (ja tem): {arq}")
        continue

    if "usuario-info" not in conteudo:
        continue

    if ">Configura" in conteudo:
        conteudo = conteudo.replace(
            '<a href="/configuracoes"',
            link + '                <a href="/configuracoes"',
            1
        )
    elif ">Sair<" in conteudo:
        conteudo = conteudo.replace(
            '<a href="/logout"',
            link + '                <a href="/logout"',
            1
        )
    else:
        print(f"Sem menu: {arq}")
        continue

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print(f"OK: {arq}")

print("\nPronto.")
