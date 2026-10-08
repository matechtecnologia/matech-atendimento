with open("consultor_rotas.py", "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace(
    'LIMITES_DIARIOS = {\n    "gratis": 5,\n    "basico": 20,\n    "pro": 60,\n    "empresarial": 200,\n}',
    'LIMITES_DIARIOS = {\n    "gratis": 5,\n    "basico": 20,\n    "pro": 60,\n    "empresarial": 200,\n    "admin": 99999,\n}'
)

with open("consultor_rotas.py", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - plano admin adicionado")
