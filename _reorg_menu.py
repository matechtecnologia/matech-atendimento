import re
with open("plano_ui.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

antigo = '''def _topo(ativo):
    itens = [
        ("/plano", "Dashboard", "dashboard"),
        ("/plano/fases", "Roadmap", "fases"),
        ("/plano/metas", "Metas", "metas"),
        ("/plano/tarefas", "Tarefas", "tarefas"),
        ("/plano/comercial", "Comercial", "comercial"),
        ("/plano/produtos", "Produtos", "produtos"),
        ("/plano/projetos", "Projetos", "projetos"),
        ("/plano/gestao", "Gestao", "gestao"),
        ("/plano/lab", "Lab", "lab"),
        ("/plano/decisoes", "Decisoes", "decisoes"),
        ("/plano/financeiro", "Financeiro", "financeiro"),
        ("/plano/roi", "ROI", "roi"),
        ("/plano/relatorios", "Relatorios", "relatorios"),
        ("/plano/bloqueios", "Bloqueios", "bloqueios"),
        ("/plano/pendencias", "Pendencias", "pendencias"),
        ("/plano/proximos", "Proximos", "proximos"),
        ("/plano/diario", "Diario", "diario"),
    ]
    menu = "".join(
        f'<a href="{href}" class="{"ativo" if ativo==key else ""}">{nome}</a>'
        for href, nome, key in itens
    )'''

novo = '''def _topo(ativo):
    grupos = [
        ("PAINEL", [
            ("/plano", "Dashboard", "dashboard"),
            ("/plano/fases", "Roadmap", "fases"),
            ("/plano/metas", "Metas", "metas"),
            ("/plano/tarefas", "Tarefas", "tarefas"),
        ]),
        ("PRODUTO", [
            ("/plano/produtos", "Produtos", "produtos"),
            ("/plano/projetos", "Projetos", "projetos"),
            ("/plano/lab", "Lab", "lab"),
            ("/plano/decisoes", "Decisoes", "decisoes"),
        ]),
        ("OPERACAO", [
            ("/plano/comercial", "Comercial", "comercial"),
            ("/plano/gestao", "Gestao", "gestao"),
            ("/plano/financeiro", "Financeiro", "financeiro"),
            ("/plano/roi", "ROI", "roi"),
            ("/plano/relatorios", "Relatorios", "relatorios"),
        ]),
        ("SISTEMA", [
            ("/plano/bloqueios", "Bloqueios", "bloqueios"),
            ("/plano/pendencias", "Pendencias", "pendencias"),
            ("/plano/proximos", "Proximos", "proximos"),
            ("/plano/diario", "Diario", "diario"),
        ]),
    ]
    partes = []
    for nome_grupo, itens in grupos:
        links = "".join(
            f'<a href="{href}" class="{"ativo" if ativo==key else ""}">{nome}</a>'
            for href, nome, key in itens
        )
        partes.append(f'<div class="grupo"><span class="grupo-label">{nome_grupo}</span>{links}</div>')
    menu = "".join(partes)'''

if antigo in conteudo:
    conteudo = conteudo.replace(antigo, novo)
    with open("plano_ui.py", "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("OK - menu reorganizado")
else:
    print("ERRO - nao achei o bloco antigo")
