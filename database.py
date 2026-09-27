import sqlite3
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def criar_banco():
    conn = sqlite3.connect("dados.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'atendente',
            ativo INTEGER NOT NULL DEFAULT 1,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER UNIQUE NOT NULL,
            plano TEXT DEFAULT 'gratis',
            onboarding_completo INTEGER DEFAULT 0,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nichos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendedor_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            produto TEXT,
            publico TEXT,
            preco TEXT,
            dor TEXT,
            objecao TEXT,
            diferencial TEXT,
            tom TEXT,
            prompt_gerado TEXT,
            ativo INTEGER DEFAULT 1,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS atendimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            atendente_id INTEGER NOT NULL,
            nicho_id INTEGER,
            whatsapp TEXT,
            linha_crm TEXT,
            mensagem_cliente TEXT,
            o_que_falar TEXT,
            texto_para_enviar TEXT,
            acao_crm TEXT,
            linha_crm_gerada TEXT,
            status TEXT DEFAULT 'processando',
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            whatsapp TEXT NOT NULL,
            vendedor_id INTEGER NOT NULL,
            direcao TEXT NOT NULL,
            mensagem TEXT NOT NULL,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendedor_id INTEGER NOT NULL,
            whatsapp TEXT NOT NULL,
            nome TEXT,
            email TEXT,
            origem TEXT,
            status TEXT DEFAULT 'lead',
            observacoes TEXT,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(vendedor_id, whatsapp)
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hist_whatsapp ON historico(whatsapp, vendedor_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clientes_vendedor ON clientes(vendedor_id)")

    conn.commit()
    conn.close()
    print("Banco criado: dados.db")

if __name__ == "__main__":
    criar_banco()