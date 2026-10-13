# 1. Remove o CSS "FORCAR BOTAO IA APARECER" (que faz o cabeçalho PC aparecer em mobile)
with open("templates/resultado.html", "r", encoding="utf-8") as f:
    c = f.read()

inicio = c.find('        /* FORCAR BOTAO IA APARECER */')
if inicio != -1:
    # Encontra o </style> depois
    fim = c.find('</style>', inicio)
    if fim != -1:
        c = c[:inicio] + '    ' + c[fim:]
        print("OK - removido FORCAR BOTAO IA APARECER")

with open("templates/resultado.html", "w", encoding="utf-8") as f:
    f.write(c)

# 2. Inverte ordem: IA antes do "?"
with open("static/app-mobile.js", "r", encoding="utf-8") as f:
    m = f.read()

# A ordem ATUAL eh: [help] [ia] - preciso trocar pra [ia] [help]
antigo = '''            <button class="app-help-btn" id="app-help-btn" aria-label="Ajuda" title="Ajuda">
                ${window.ICONE ? window.ICONE('ajuda', { tamanho: 22 }) : '?'}
            </button>
            <button class="app-ia-btn" id="app-ia-btn" aria-label="IA Aprende" title="IA Aprende: ligar/desligar">
                <span class="app-ia-icone">🧠</span>
                <span class="app-ia-dot" id="app-ia-dot"></span>
            </button>'''

novo = '''            <button class="app-ia-btn" id="app-ia-btn" aria-label="IA Aprende" title="IA Aprende: ligar/desligar">
                <span class="app-ia-icone">🧠</span>
                <span class="app-ia-dot" id="app-ia-dot"></span>
            </button>
            <button class="app-help-btn" id="app-help-btn" aria-label="Ajuda" title="Ajuda">
                ${window.ICONE ? window.ICONE('ajuda', { tamanho: 22 }) : '?'}
            </button>'''

if antigo in m:
    m = m.replace(antigo, novo, 1)
    with open("static/app-mobile.js", "w", encoding="utf-8") as f:
        f.write(m)
    print("OK - ordem trocada: [menu] [logo] [IA] [?]")
else:
    print("AVISO - nao achei o bloco de botoes")

print("OK - arquivo salvo")
