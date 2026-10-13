with open("templates/resultado.html", "r", encoding="utf-8") as f:
    c = f.read()

# Remove o botao do HTML
c = c.replace(
    '''<input type="checkbox" id="toggle-ia-aprende" style="display:none;">
            <button type="button" class="btn-ia" id="ia-btn-header" title="IA Aprende: ligar/desligar">
                <span class="btn-ia-icone">🧠</span>
                <span class="btn-ia-txt">IA Aprende</span>
                <span class="btn-ia-status">
                    <span class="dot"></span>
                    <span id="ia-btn-estado">OFF</span>
                </span>
            </button>
            ''',
    ''
)

# Remove o CSS do botao
inicio = c.find('        /* BOTAO IA APRENDE - DESIGN SOFISTICADO */')
if inicio != -1:
    fim = c.find('        @media (max-width: 768px)', inicio)
    if fim != -1:
        c = c[:inicio] + c[fim:]

# Remove media query mobile do botao
inicio2 = c.find('        @media (max-width: 768px) {', c.find('/* BOTAO IA APRENDE'))
if inicio2 != -1:
    fim2 = c.find('        @media (max-width: 480px) {', inicio2)
    if fim2 != -1:
        c = c[:inicio2] + c[fim2:]

with open("templates/resultado.html", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - resultado.html revertido")
