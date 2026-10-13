with open("templates/resultado.html", "r", encoding="utf-8") as f:
    c = f.read()

# Remove a classe bloco-wrap do bloco da IA (pra aparecer sempre)
c = c.replace(
    '<div class="bloco bloco-wrap" id="bloco-ia-aprende"',
    '<div class="bloco aberto" id="bloco-ia-aprende"'
)

with open("templates/resultado.html", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - bloco IA sempre visivel")
