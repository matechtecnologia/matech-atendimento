import app
c = app.get_conn()
cur = c.cursor()

# Atualiza o nicho 14
cur.execute("""
    UPDATE nichos SET 
        produto = %s,
        publico = %s,
        preco = %s,
        dor = %s,
        objecao = %s,
        diferencial = %s,
        tom = %s
    WHERE id = 14
""", (
    "Sistema de atendimento comercial com IA. O vendedor cola a mensagem que recebeu no WhatsApp e a IA devolve 3 blocos: O QUE FALAR (audio pronto), TEXTO PARA ENVIAR e o ESTAGIO do lead. A IA lembra do historico, registra o lead automaticamente, agenda o follow-up e mostra quem precisa de atencao.",
    "Pequenos vendedores que atendem no WhatsApp. Corretores de imoveis, seguros e consorcio. Vendedores de carro e moto. Consultores. Mentores. Prestadores de servico. Donos de loja pequena que vendem pelo WhatsApp.",
    "Gratis R$ 0 / 150 interacoes por mes. Basico R$ 97/mes / 1.500 interacoes. Pro R$ 297/mes / 4.500 interacoes. Empresarial R$ 597/mes / 9.000 interacoes. Primeiro mes com 50% de desconto.",
    "O vendedor recebe mensagem no WhatsApp e nao sabe o que responder. Trava. Demora. Responde errado. Perde o timing. Esquece de dar follow-up. Nao sabe em que estagio o lead esta. Nao tem historico organizado. Perde cliente pro concorrente mais rapido. Esta sozinho, sem chefe nem equipe pra treinar.",
    "Ja uso ChatGPT pra isso. R$ 97 e caro pra mim. Nao tenho tempo de aprender sistema novo. Meus clientes sao poucos. Vou testar depois. Meu concorrente nao usa e vende igual. Nao sei se a IA vai entender meu negocio.",
    "O M.A Tech NAO le WhatsApp automaticamente. O vendedor cola a mensagem manualmente no sistema, pega a resposta sugerida e envia pelo WhatsApp em audio ou texto. NAO tem integracao com WhatsApp, NAO tem QR code, NAO le conversas sozinho. Mas registra o lead, agenda o follow-up e lembra do historico automaticamente.",
    "Direto. Pratico. Sem enrolacao. Fala como vendedor experiente. Linguagem de WhatsApp. Zero formalidade. Foca em acao. O que fazer agora. Nao fica filosofando."
))

c.commit()
print("OK - nicho 14 atualizado")
cur.close()
app.close_conn(c)
