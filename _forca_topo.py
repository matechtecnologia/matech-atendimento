with open("templates/resultado.html", "r", encoding="utf-8") as f:
    c = f.read()

# Forca o topo a aparecer em mobile
forca = '''
<style>
@media (max-width: 768px) {
    .container-atendimento > .topo,
    body .topo,
    .topo {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        width: 100% !important;
        height: auto !important;
        min-height: 48px !important;
    }
}
</style>
'''

if "display: flex !important" not in c or ".container-atendimento > .topo" not in c:
    c = c.replace("</head>", forca + "\n</head>", 1)
    with open("templates/resultado.html", "w", encoding="utf-8") as f:
        f.write(c)
    print("OK - forcado .topo aparecer em mobile")
else:
    print("AVISO - ja estava")
