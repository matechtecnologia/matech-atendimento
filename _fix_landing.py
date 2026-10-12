with open("templates/landing.html", "r", encoding="utf-8") as f:
    c = f.read()

# Trocar valores dos planos
c = c.replace('300 RESPOSTAS/MÊS', '150 RESPOSTAS/MÊS · 1 conversa/dia')
c = c.replace('3.000 RESPOSTAS/MÊS', '1.500 RESPOSTAS/MÊS · 10 conversas/dia')
c = c.replace('10.000 RESPOSTAS/MÊS', '4.500 RESPOSTAS/MÊS · 30 conversas/dia')
c = c.replace('30.000 RESPOSTAS/MÊS', '9.000 RESPOSTAS/MÊS · 60 conversas/dia')

# Trocar excedente
c = c.replace('Excedente: R$ 0,05/resposta', 'Excedente: R$ 0,10/resposta')
c = c.replace('Excedente: R$ 0,04/resposta', 'Excedente: R$ 0,10/resposta')
c = c.replace('Excedente: R$ 0,03/resposta', 'Excedente: R$ 0,10/resposta')

# Adicionar aviso de desconto no 1o mes (abaixo dos cards)
c = c.replace(
    '<div class="plan featured">',
    '<div class="plan featured">'
)

# Ajustar o FAQ sobre excedente
c = c.replace(
    'Nada trava. Você',
    'Nada trava até 120% do limite. Você'
)

with open("templates/landing.html", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - landing atualizada")
