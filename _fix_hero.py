with open("templates/landing.html", "r", encoding="utf-8") as f:
    c = f.read()

# 1. Title
c = c.replace(
    '<title>M.A Tech — Atendimento com IA no WhatsApp</title>',
    '<title>M.A Tech — A IA que te ajuda a atender no WhatsApp</title>'
)

# 2. Meta description
c = c.replace(
    '<meta name="description" content="A IA que atende seus clientes no WhatsApp e te diz exatamente o que falar, o que enviar e qual o estágio do lead.">',
    '<meta name="description" content="A IA que te ajuda a atender no WhatsApp. Você cola a mensagem do cliente, ela te diz exatamente o que falar, o que enviar e qual o próximo passo.">'
)

# 3. Hero - badge
c = c.replace(
    '<div class="badge">🤖 IA treinada no SEU negócio</div>',
    '<div class="badge">🤖 IA treinada no seu negócio</div>'
)

# 4. Hero - H1
c = c.replace(
    '<h1>Sua IA atende no WhatsApp e te diz <em>exatamente o que falar</em></h1>',
    '<h1>A IA te ajuda a atender no WhatsApp e te diz <em>exatamente o que falar</em></h1>'
)

# 5. Hero - subtitulo
c = c.replace(
    '<p>Você configura seu negócio uma vez. A IA assume cada conversa, analisa o histórico do cliente e devolve 3 blocos prontos: áudio pra gravar, texto pra enviar e o estágio do lead atualizado.</p>',
    '<p>Você configura seu negócio uma vez. Cada vez que um cliente te manda mensagem, você cola aqui. A IA analisa o histórico e devolve 3 blocos prontos: <strong style="color:#e8e8e8;">o que falar</strong> (em áudio natural), <strong style="color:#e8e8e8;">o texto pronto</strong> pra enviar e o <strong style="color:#e8e8e8;">estágio do lead</strong> atualizado.</p>'
)

with open("templates/landing.html", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - hero atualizado")
