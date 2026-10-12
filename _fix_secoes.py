with open("templates/landing.html", "r", encoding="utf-8") as f:
    c = f.read()

# 1. Ajustar "Como funciona"
c = c.replace(
    '<p class="sub">Três passos. Menos de 5 minutos. Sem instalar nada.</p>',
    '<p class="sub">Três passos. Você continua atendendo do seu jeito. A IA só te ajuda a não travar.</p>'
)

# 2. Ajustar passo 3
c = c.replace(
    '<h3>Cole a mensagem, receba a resposta</h3>',
    '<h3>Cole a mensagem e receba a resposta</h3>'
)

# 3. Ajustar a seção "Por que vendedores usam" (sub)
c = c.replace(
    '<p class="sub">Não é chatbot genérico. É uma IA treinada no seu negócio.</p>',
    '<p class="sub">Não é chatbot que responde sozinho. É uma IA treinada no SEU negócio, que te ajuda a vender mais.</p>'
)

# 4. Ajustar card "Pronta pra áudio"
c = c.replace(
    '<h3>Pronta pra áudio</h3><p>O bloco "o que falar" vem em linguagem natural, do jeito que você gravaria. É só ler e apertar o microfone.</p>',
    '<h3>Áudio pronto</h3><p>O bloco "o que falar" vem em linguagem natural, do jeito que você gravaria. É só ler e apertar o microfone do WhatsApp.</p>'
)

# 5. Ajustar card "CRM sem esforço"
c = c.replace(
    '<h3>CRM sem esforço</h3><p>Cada resposta atualiza o estágio do cliente automaticamente: Novo Lead → Em Atendimento → Negociação → Cliente.</p>',
    '<h3>CRM automático</h3><p>Cada resposta atualiza o estágio do cliente automaticamente: Novo Lead → Em Atendimento → Negociação → Cliente. Substitui planilha, bloco de notas e CRM manual.</p>'
)

with open("templates/landing.html", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - secoes ajustadas")
