# consultor_db.py
# M.A Tech — Banco da Consultoria Empresarial
# Cria as tabelas da area de Consultoria.
# Chamado por consultor_install.py
#
# 3 tabelas:
#   1. consultorias          — uma por vendedor (sessao ativa)
#   2. consultoria_mensagens — historico da conversa (IA <-> cliente)
#   3. consultoria_uso       — contador diario (limite por plano)


def inicializar_consultor(get_conn, close_conn):
    """Cria as tabelas da Consultoria. Idempotente (IF NOT EXISTS)."""

    conn = get_conn()
    cur = conn.cursor()

    # ============================================================
    # 1. CONSULTORIAS — uma por vendedor (sessao de consultoria)
    # ============================================================
    cur.execute("""CREATE TABLE IF NOT EXISTS consultorias (
        id SERIAL PRIMARY KEY,
        vendedor_id INTEGER NOT NULL REFERENCES vendedores(id) ON DELETE CASCADE,
        status TEXT DEFAULT 'ativa',
        gargalo_detectado TEXT,
        servico_indicado TEXT,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    # ============================================================
    # 2. CONSULTORIA_MENSAGENS — historico da conversa
    # ============================================================
    cur.execute("""CREATE TABLE IF NOT EXISTS consultoria_mensagens (
        id SERIAL PRIMARY KEY,
        consultoria_id INTEGER NOT NULL REFERENCES consultorias(id) ON DELETE CASCADE,
        direcao TEXT NOT NULL,
        mensagem TEXT NOT NULL,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""")

    # ============================================================
    # 3. CONSULTORIA_USO — contador diario (limite por plano)
    # ============================================================
    cur.execute("""CREATE TABLE IF NOT EXISTS consultoria_uso (
        id SERIAL PRIMARY KEY,
        vendedor_id INTEGER NOT NULL REFERENCES vendedores(id) ON DELETE CASCADE,
        data DATE NOT NULL DEFAULT CURRENT_DATE,
        total INTEGER DEFAULT 0,
        UNIQUE(vendedor_id, data)
    )""")

    # ============================================================
    # INDICES (aceleram as buscas mais comuns)
    # ============================================================
    cur.execute("""CREATE INDEX IF NOT EXISTS idx_consultorias_vendedor
        ON consultorias(vendedor_id)""")

    cur.execute("""CREATE INDEX IF NOT EXISTS idx_consultoria_mensagens_consultoria
        ON consultoria_mensagens(consultoria_id)""")

    cur.execute("""CREATE INDEX IF NOT EXISTS idx_consultoria_uso_vendedor_data
        ON consultoria_uso(vendedor_id, data)""")

    conn.commit()
    cur.close()
    close_conn(conn)
    print("Consultor DB: tabelas OK")