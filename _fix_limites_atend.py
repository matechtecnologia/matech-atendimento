with open("app.py", "r", encoding="utf-8") as f:
    c = f.read()

# Troca os valores
c = c.replace(
    'LIMITES_RESPOSTAS = {"gratis": 300, "basico": 3000, "pro": 10000, "empresarial": 30000}',
    'LIMITES_RESPOSTAS = {"gratis": 150, "basico": 1500, "pro": 4500, "empresarial": 9000}'
)

c = c.replace(
    'EXCEDENTE_PRECO = {"gratis": 0.0, "basico": 0.05, "pro": 0.04, "empresarial": 0.03}',
    'EXCEDENTE_PRECO = {"gratis": 0.0, "basico": 0.10, "pro": 0.10, "empresarial": 0.10}'
)

# Adiciona desconto do 1o mes
c = c.replace(
    'PLANOS_PRECO = {"basico": 97.0, "pro": 297.0, "empresarial": 597.0}',
    '''PLANOS_PRECO = {"basico": 97.0, "pro": 297.0, "empresarial": 597.0}
PLANOS_PRECO_1MES = {"basico": 47.0, "pro": 147.0, "empresarial": 297.0}'''
)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - valores atualizados")
