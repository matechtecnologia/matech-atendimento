with open("static/app-mobile.js", "r", encoding="utf-8") as f:
    c = f.read()

# Troca o grid de 3 colunas pra 4 colunas
c = c.replace(
    'grid-template-columns: 44px 1fr 44px !important;',
    'grid-template-columns: 44px 1fr 44px 44px !important;'
)

with open("static/app-mobile.js", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - grid de 4 colunas")
