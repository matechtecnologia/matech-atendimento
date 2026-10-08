# completar_plano.py
# Adiciona SÓ o que falta nas tabelas vazias.
# Nao mexe no que ja existe.

import app
c = app.get_conn()
cur = c.cursor()

print("Completando Plano...")

# ============================================================
# PROJECTS — 4 projetos
# ============================================================
cur.execute("SELECT COUNT(*) FROM projects")
if cur.fetchone()[0] == 0:
    projetos = [
        ("Popular as 17 telas do Plano", "Preencher tabelas do Plano com conteudo real", "em_andamento", "alta", 30),
        ("Migrar Asaas para producao", "Sair do sandbox e aceitar PIX real", "planejado", "critica", 0),
        ("Landing page publicada", "Site de vendas em matech.com.br", "planejado", "critica", 0),
        ("Comprar dominio matech.com.br", "Registro no Registro.br + DNS no Render", "planejado", "alta", 0),
    ]
    for p in projetos:
        cur.execute("""INSERT INTO projects (nome, descricao, status, prioridade, percentual)
                       VALUES (%s, %s, %s, %s, %s)""", p)
    print(f"  projects: {len(projetos)} projetos adicionados")
else:
    print("  projects: ja tem dados, pulando")

# ============================================================
# DECISIONS — 3 decisoes (com coluna titulo)
# ============================================================
cur.execute("SELECT COUNT(*) FROM decisions")
if cur.fetchone()[0] == 0:
    decisoes = [
        ("Centralizar gestao no Chat 7", "Allan decidiu ter 1 so chat gestor", "Ter 3 chats em paralelo", "Aumentar produtividade", "em_teste"),
        ("Popular tabelas do Plano com conteudo dos 10 documentos", "Telas estavam vazias", "Deixar vazio", "Telas com conteudo real", "em_execucao"),
        ("Manter plano_ui.py e aposentar plano_rotas.py", "plano_ui venceu na pratica", "Unificar os dois", "Remover duplicacao", "planejada"),
    ]
    for d in decisoes:
        cur.execute("""INSERT INTO decisions (titulo, decisao, motivo, alternativas, impacto_esperado, status)
                       VALUES (%s, %s, %s, %s, %s, %s)""", d)
    print(f"  decisions: {len(decisoes)} decisoes adicionadas")
else:
    print("  decisions: ja tem dados, pulando")

# ============================================================
# METRICS — 6 metricas
# ============================================================
cur.execute("SELECT COUNT(*) FROM metrics")
if cur.fetchone()[0] == 0:
    metricas = [
        ("Usuarios cadastrados", "produto", 5, "unidade"),
        ("Clientes pagantes", "comercial", 0, "unidade"),
        ("MRR", "financeiro", 0, "R$"),
        ("Consultorias realizadas", "produto", 6, "unidade"),
        ("Atendimentos gerados", "produto", 0, "unidade"),
        ("Nichos cadastrados", "produto", 0, "unidade"),
    ]
    for m in metricas:
        cur.execute("""INSERT INTO metrics (nome, categoria, valor, unidade)
                       VALUES (%s, %s, %s, %s)""", m)
    print(f"  metrics: {len(metricas)} metricas adicionadas")
else:
    print("  metrics: ja tem dados, pulando")

# ============================================================
# BLOCKERS — adicionar 2 (o 1 existente e do boot)
# ============================================================
cur.execute("SELECT COUNT(*) FROM blockers WHERE titulo LIKE '%CNPJ%'")
if cur.fetchone()[0] == 0:
    novos_bloqueios = [
        ("Sem CNPJ", "Nao da pra usar Asaas producao sem CNPJ", "Alto - bloqueia pagamento real", "Abrir CNPJ ou usar MEI", "critica"),
        ("Bug de login em /plano", "Cookie nao esta sendo enviado corretamente", "Medio - bloqueia acesso ao Plano", "Investigar middleware de auth", "alta"),
    ]
    for b in novos_bloqueios:
        cur.execute("""INSERT INTO blockers (titulo, problema, impacto, solucao_necessaria, prioridade)
                       VALUES (%s, %s, %s, %s, %s)""", b)
    print(f"  blockers: {len(novos_bloqueios)} bloqueios adicionados")
else:
    print("  blockers: ja tem CNPJ registrado, pulando")

c.commit()
cur.close()
app.close_conn(c)

print()
print("PRONTO.")
