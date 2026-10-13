with open("templates/hub.html", "r", encoding="utf-8") as f:
    c = f.read()

# Trocar "Bem-vindo de volta" por "Bem-vindo"
c = c.replace(
    '<h2>Bem-vindo de volta, {{ usuario_nome.split()[0] if usuario_nome else "vendedor" }} 👋</h2>',
    '<h2>Bem-vindo, {{ usuario_nome.split()[0] if usuario_nome else "vendedor" }} 👋</h2>'
)

with open("templates/hub.html", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - hub ajustado")
