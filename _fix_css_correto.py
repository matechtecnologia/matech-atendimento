with open("templates/resultado.html", "r", encoding="utf-8") as f:
    c = f.read()

# Adiciona CSS limpo
css_limpo = '''
<style>
/* BOTAO IA NO RESULTADO - VISIVEL NO MOBILE SEM QUEBRAR O RESTO */
@media (max-width: 768px) {
    /* O header mobile (.app-header) cuida do layout */
    /* O .topo do PC deve ficar escondido em mobile */
    .container-atendimento .topo {
        display: none !important;
    }
}
</style>
'''

# Insere antes de </head>
if ".container-atendimento .topo" not in c:
    c = c.replace("</head>", css_limpo + "\n</head>", 1)
    with open("templates/resultado.html", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - CSS correto adicionado (esconde topo em mobile)")
else:
    print("AVISO - ja estava")
