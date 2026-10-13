with open("templates/resultado.html", "r", encoding="utf-8") as f:
    c = f.read()

# Troca o aid
c = c.replace("const aid = {{ atendimento_id }};", "const aid = {{ atendimento.id }};")

with open("templates/resultado.html", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - aid corrigido")
