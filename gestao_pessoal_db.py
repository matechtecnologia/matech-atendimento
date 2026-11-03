# ============================================
# M.A Tech - Gestao Pessoal Financeira (DB)
# ============================================
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

CATEGORIAS_ENTRADA = ["Salário", "Freelance", "Investimento", "Venda", "Outros"]
CATEGORIAS_SAIDA_ESSENCIAL = ["Moradia", "Alimentação", "Transporte", "Saúde", "Educação"]
CATEGORIAS_SAIDA_NAO_ESSENCIAL = ["Lazer", "Roupas", "Eletrônicos", "Assinaturas"]

TIPOS_CAIXINHA = ["emergencia", "investimento", "lazer", "objetivo"]
STATUS_LANCAMENTO = ["concluido", "planejado"]


def _conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def init_gestao_pessoal():
    """Cria as tabelas do modulo Gestao Pessoal Financeira."""
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS gestao_pessoal_lancamentos (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER NOT NULL,
                    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('entrada', 'saida')),
                    valor NUMERIC(12,2) NOT NULL,
                    categoria VARCHAR(50) NOT NULL,
                    essencial BOOLEAN DEFAULT FALSE,
                    descricao TEXT,
                    data DATE NOT NULL DEFAULT CURRENT_DATE,
                    criado_em TIMESTAMP DEFAULT NOW(),
                    status VARCHAR(20) NOT NULL DEFAULT 'concluido',
                    data_prevista DATE,
                    data_conclusao DATE
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_gp_lanc_usuario ON gestao_pessoal_lancamentos(usuario_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_gp_lanc_data ON gestao_pessoal_lancamentos(data DESC)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_gp_lanc_status ON gestao_pessoal_lancamentos(status)")

            # Migracoes idempotentes pra bases antigas
            cur.execute("ALTER TABLE gestao_pessoal_lancamentos ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'concluido'")
            cur.execute("ALTER TABLE gestao_pessoal_lancamentos ADD COLUMN IF NOT EXISTS data_prevista DATE")
            cur.execute("ALTER TABLE gestao_pessoal_lancamentos ADD COLUMN IF NOT EXISTS data_conclusao DATE")

            cur.execute("""
                CREATE TABLE IF NOT EXISTS gestao_pessoal_metas (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER NOT NULL,
                    titulo VARCHAR(120) NOT NULL,
                    valor_meta NUMERIC(12,2) NOT NULL,
                    valor_atual NUMERIC(12,2) DEFAULT 0,
                    prazo DATE,
                    criado_em TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_gp_metas_usuario ON gestao_pessoal_metas(usuario_id)")

            cur.execute("""
                CREATE TABLE IF NOT EXISTS gestao_pessoal_reserva (
                    usuario_id INTEGER PRIMARY KEY,
                    valor_atual NUMERIC(12,2) DEFAULT 0,
                    meta NUMERIC(12,2) DEFAULT 0,
                    atualizado_em TIMESTAMP DEFAULT NOW()
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS gestao_caixinhas (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER NOT NULL,
                    tipo VARCHAR(20) NOT NULL,
                    valor_atual NUMERIC(14,2) NOT NULL DEFAULT 0,
                    instituicao_financeira VARCHAR(120),
                    criado_em TIMESTAMP DEFAULT NOW(),
                    UNIQUE (usuario_id, tipo)
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_gp_caixinhas_usuario ON gestao_caixinhas(usuario_id)")

            cur.execute("""
                CREATE TABLE IF NOT EXISTS gestao_aplicacoes (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER NOT NULL,
                    caixinha_tipo VARCHAR(20) NOT NULL,
                    valor NUMERIC(14,2) NOT NULL,
                    porcentagem_aplicada NUMERIC(6,2),
                    instituicao_financeira VARCHAR(120),
                    data DATE NOT NULL,
                    criado_em TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_gp_aplicacoes_usuario ON gestao_aplicacoes(usuario_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_gp_aplicacoes_tipo ON gestao_aplicacoes(usuario_id, caixinha_tipo, data DESC)")
        conn.commit()
    print("Gestao Pessoal DB: tabelas OK")
