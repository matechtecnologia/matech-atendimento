with open("templates/resultado.html", "r", encoding="utf-8") as f:
    c = f.read()

# 1. Remove o bloco de CSS do btn-ia que esta depois do botao
inicio_css = c.find('        <style>\n        /* BOTAO IA APRENDE - DESIGN SOFISTICADO */')
fim_css = c.find('        </style>', inicio_css)

if inicio_css != -1 and fim_css != -1:
    # Pega so o CSS do btn-ia (sem aviso)
    css_btn = c[inicio_css:fim_css]
    # Remove o bloco todo
    c = c[:inicio_css] + c[fim_css + len('        </style>'):]
    print("OK - CSS do botao removido do lugar errado")
else:
    css_btn = ""
    print("AVISO - nao achou CSS para mover")

# 2. Mover o botao pra FORA do usuario-info
antigo_botao = '''            <div class="usuario-info">
                <input type="checkbox" id="toggle-ia-aprende" style="display:none;">
                <button type="button" class="btn-ia" id="ia-btn-header" title="IA Aprende: ligar/desligar">
                    <span class="btn-ia-icone">🧠</span>
                    <span class="btn-ia-txt">IA Aprende</span>
                    <span class="btn-ia-status">
                        <span class="dot"></span>
                        <span id="ia-btn-estado">OFF</span>
                    </span>
                </button>
                <span class="usuario-nome">{{ usuario_nome }}</span>'''

novo_botao = '''            <input type="checkbox" id="toggle-ia-aprende" style="display:none;">
            <button type="button" class="btn-ia" id="ia-btn-header" title="IA Aprende: ligar/desligar">
                <span class="btn-ia-icone">🧠</span>
                <span class="btn-ia-txt">IA Aprende</span>
                <span class="btn-ia-status">
                    <span class="dot"></span>
                    <span id="ia-btn-estado">OFF</span>
                </span>
            </button>
            <div class="usuario-info">
                <span class="usuario-nome">{{ usuario_nome }}</span>'''

if antigo_botao in c:
    c = c.replace(antigo_botao, novo_botao, 1)
    print("OK - botao movido pra fora do usuario-info")
else:
    print("AVISO - botao nao achado")

with open("templates/resultado.html", "w", encoding="utf-8") as f:
    f.write(c)

print("OK - arquivo salvo")
