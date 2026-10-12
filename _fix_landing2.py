with open("templates/landing.html", "r", encoding="utf-8") as f:
    c = f.read()

# 1. FAQ excedente
c = c.replace(
    'Você continua usando, e cobramos um valor pequeno por resposta excedente: R$ 0,05 no Básico, R$ 0,04 no Pro, R$ 0,03 no Empresarial. O valor aparece na próxima fatura, sem surpresa.',
    'Você continua usando, e cobramos R$ 0,10 por resposta excedente (mesmo valor em todos os planos). Acima de 120% do limite, o sistema pausa e você pode fazer upgrade ou comprar um pacote extra. Sem surpresa, sem travar no meio de uma conversa.'
)

# 2. Adicionar desconto nos cards (Básico)
c = c.replace(
    '''<h3>Básico</h3>
        <div class="price">R$ 97<small>/mês</small></div>''',
    '''<h3>Básico</h3>
        <div class="price">R$ 97<small>/mês</small></div>
        <div style="color:#00d97e;font-size:12px;font-weight:700;margin-bottom:8px;">1º mês R$ 47</div>'''
)

# 3. Adicionar desconto nos cards (Pro)
c = c.replace(
    '''<h3>Pro</h3>
        <div class="price">R$ 297<small>/mês</small></div>''',
    '''<h3>Pro</h3>
        <div class="price">R$ 297<small>/mês</small></div>
        <div style="color:#00d97e;font-size:12px;font-weight:700;margin-bottom:8px;">1º mês R$ 147</div>'''
)

# 4. Adicionar desconto nos cards (Empresarial)
c = c.replace(
    '''<h3>Empresarial</h3>
        <div class="price">R$ 597<small>/mês</small></div>''',
    '''<h3>Empresarial</h3>
        <div class="price">R$ 597<small>/mês</small></div>
        <div style="color:#00d97e;font-size:12px;font-weight:700;margin-bottom:8px;">1º mês R$ 297</div>'''
)

# 5. Empresarial botao
c = c.replace(
    '<a href="/signup" class="btn btn-ghost">Falar com vendas</a>',
    '<a href="/signup" class="btn btn-ghost">Assinar Empresarial</a>'
)

# 6. Botao Basico
c = c.replace(
    '<a href="/signup" class="btn btn-ghost">Assinar</a>',
    '<a href="/signup" class="btn btn-ghost">Assinar Básico</a>'
)

with open("templates/landing.html", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - landing atualizada (5 correcoes)")
