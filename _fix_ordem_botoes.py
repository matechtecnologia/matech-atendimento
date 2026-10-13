# 1. Limpa o resultado.html - remove CSS forcado
with open("templates/resultado.html", "r", encoding="utf-8") as f:
    c = f.read()

# Remove o bloco "FORCA BOTAO IA - REGRA FINAL"
inicio1 = c.find('/* FORCA BOTAO IA - REGRA FINAL */')
if inicio1 != -1:
    # Encontra o </style> anterior
    fim1 = c.find('</style>', inicio1)
    if fim1 != -1:
        c = c[:inicio1] + c[fim1:]
        print("OK - removido FORCA BOTAO IA")

# Remove o bloco "FORCAR BOTAO MOBILE"
inicio2 = c.find('/* FORCAR BOTAO MOBILE - REGRA FINAL */')
if inicio2 != -1:
    fim2 = c.find('</style>', inicio2)
    if fim2 != -1:
        c = c[:inicio2] + c[fim2:]
        print("OK - removido FORCAR BOTAO MOBILE")

with open("templates/resultado.html", "w", encoding="utf-8") as f:
    f.write(c)

# 2. Troca ordem dos botoes no app-mobile.js
with open("static/app-mobile.js", "r", encoding="utf-8") as f:
    m = f.read()

# Tira o botao IA de onde esta
antigo_ia = '''            <button class="app-ia-btn" id="app-ia-btn" aria-label="IA Aprende" title="IA Aprende: ligar/desligar">
                <span class="app-ia-icone">🧠</span>
                <span class="app-ia-dot" id="app-ia-dot"></span>
            </button>
            <button class="app-help-btn" id="app-help-btn" aria-label="Ajuda" title="Ajuda">
                ${window.ICONE ? window.ICONE('ajuda', { tamanho: 22 }) : '?'}
            </button>'''

novo_ia = '''            <button class="app-help-btn" id="app-help-btn" aria-label="Ajuda" title="Ajuda">
                ${window.ICONE ? window.ICONE('ajuda', { tamanho: 22 }) : '?'}
            </button>
            <button class="app-ia-btn" id="app-ia-btn" aria-label="IA Aprende" title="IA Aprende: ligar/desligar">
                <span class="app-ia-icone">🧠</span>
                <span class="app-ia-dot" id="app-ia-dot"></span>
            </button>'''

if antigo_ia in m:
    m = m.replace(antigo_ia, novo_ia, 1)
    with open("static/app-mobile.js", "w", encoding="utf-8") as f:
        f.write(m)
    print("OK - ordem trocada: [menu] [logo] [?] [IA]")
else:
    print("ERRO - nao achei o bloco de botoes")

print("OK - arquivo salvo")
