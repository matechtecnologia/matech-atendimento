with open("templates/planos.html", "r", encoding="utf-8") as f:
    c = f.read()

# 1. Grátis - respostas
c = c.replace('300 RESPOSTAS/MÊS', '150 RESPOSTAS/MÊS')

# 2. Básico
c = c.replace(
    '<span style="font-size:32px; font-weight:800; color:#e8e8e8; font-family:monospace;">R$ 97</span>',
    '<span style="font-size:32px; font-weight:800; color:#e8e8e8; font-family:monospace;">R$ 97</span>'
)
c = c.replace('3.000 RESPOSTAS/MÊS', '1.500 RESPOSTAS/MÊS')
c = c.replace('+ Excedente: R$ 0,05/resposta', '+ Excedente: R$ 0,10/resposta')
c = c.replace('<input type="hidden" name="plano" value="basico">\n                    <input type="hidden" name="valor" value="97.00">', '<input type="hidden" name="plano" value="basico">')

# 3. Pro
c = c.replace('10.000 RESPOSTAS/MÊS', '4.500 RESPOSTAS/MÊS')
c = c.replace('+ Excedente: R$ 0,04/resposta', '+ Excedente: R$ 0,10/resposta')

# 4. Empresarial
c = c.replace('30.000 RESPOSTAS/MÊS', '9.000 RESPOSTAS/MÊS')
c = c.replace('+ Excedente: R$ 0,03/resposta', '+ Excedente: R$ 0,10/resposta')

# 5. Atualizar texto do "O QUE É UMA RESPOSTA"
c = c.replace(
    '''Cada vez que você cola uma mensagem do cliente e a IA devolve os 3 blocos (o que falar, o que enviar e o estágio), conta como <strong style="color:#a855f7;">1 resposta</strong>. O limite é mensal e protege você (uso abusivo) e nós (custo da IA).<br><br>
                <strong style="color:#e8e8e8;">Passou do limite?</strong> Nada trava. Cobramos um valor pequeno por resposta excedente na próxima fatura.''',
    '''Cada vez que você cola uma mensagem do cliente e a IA devolve os 3 blocos (o que falar, o que enviar e o estágio), conta como <strong style="color:#a855f7;">1 resposta</strong>. O limite é mensal e protege você (uso abusivo) e nós (custo da IA).<br><br>
                <strong style="color:#e8e8e8;">Como saber qual plano escolher?</strong><br>
                Grátis: até 1 conversa/dia<br>
                Básico: até 10 conversas/dia<br>
                Pro: até 30 conversas/dia<br>
                Empresarial: até 60 conversas/dia<br><br>
                <strong style="color:#e8e8e8;">Passou do limite?</strong> Nada trava até 120%. Cobramos R$ 0,10 por resposta excedente na próxima fatura. Acima de 120%, bloqueia e você pode fazer upgrade ou comprar respostas extras.'''
)

# 6. Adicionar aviso de desconto 1o mes no topo do container
c = c.replace(
    '<div class="container-atendimento">\n        <div class="topo">',
    '''<div class="container-atendimento">
        <div class="topo">'''
)

with open("templates/planos.html", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - planos.html atualizado")
