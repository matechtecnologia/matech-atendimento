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
                    criado_em TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_gp_lanc_usuario ON gestao_pessoal_lancamentos(usuario_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_gp_lanc_data ON gestao_pessoal_lancamentos(data DESC)")

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
        conn.commit()
    print("Gestao Pessoal DB: tabelas OK")
