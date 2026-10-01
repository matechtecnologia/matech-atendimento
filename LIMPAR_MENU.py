import io
import os
import re

TEMPLATES = [
    'clientes.html', 'cliente_detalhe.html', 'atendimento_cliente.html',
    'relatorios.html', 'followups.html', 'meus_nichos.html', 'novo_nicho.html',
    'planos.html', 'assinar.html', 'pagamento_pix.html', 'bem_vindo.html',
    'admin.html', 'admin_vendedor.html', 'admin_leads.html',
    'admin_dashboard.html', 'resultado.html', 'configuracoes.html',
    'indicar.html', 'onboarding.html',
]

# Padroes dos 4 links que vao sair
padroes = [
    r'\s*<a href="/clientes"[^>]*>.*?</a>',
    r'\s*<a href="/relatorios"[^>]*>.*?</a>',
    r'\s*<a href="/meus_nichos"[^>]*>.*?</a>',
    r'\s*<a href="/followups"[^>]*>.*?</a>',
]

total_mudou = 0

for nome in TEMPLATES:
    path = os.path.join('templates', nome)
    if not os.path.exists(path):
        continue

    with io.open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    original = c

    for p in padroes:
        # So remove se estiver dentro do .usuario-info
        # Busca o bloco usuario-info e limpa dentro dele
        pass

    # Metodo cirurgico: encontra o bloco .usuario-info e remove os links dentro dele
    def limpar_usuario_info(match):
        bloco = match.group(0)
        for p in padroes:
            bloco = re.sub(p, '', bloco, flags=re.DOTALL)
        return bloco

    c = re.sub(
        r'<div\s+class="usuario-info">.*?</div>',
        limpar_usuario_info,
        c,
        flags=re.DOTALL
    )

    if c != original:
        with io.open(path, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f'OK: {nome}')
        total_mudou += 1

print(f'\n{total_mudou} template(s) atualizado(s)')