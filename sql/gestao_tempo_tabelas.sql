-- ============================================
-- M.A Tech - Gestao Pessoal do Tempo
-- Tabelas base
-- ============================================

CREATE TABLE IF NOT EXISTS gestao_tempo_compromissos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    descricao TEXT,
    data DATE NOT NULL,
    hora_inicio TIME,
    hora_fim TIME,
    local TEXT,
    categoria TEXT,
    prioridade TEXT DEFAULT 'media',
    concluido BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_gt_comp_uid_data ON gestao_tempo_compromissos (usuario_id, data);

CREATE TABLE IF NOT EXISTS gestao_tempo_rotinas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    dia_semana INTEGER,
    hora_inicio TIME,
    hora_fim TIME,
    categoria TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_gt_rot_uid ON gestao_tempo_rotinas (usuario_id, ativo);

CREATE TABLE IF NOT EXISTS gestao_tempo_bloqueios (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    titulo TEXT DEFAULT 'Foco',
    data DATE NOT NULL,
    hora_inicio TIME,
    hora_fim TIME,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_gt_bloq_uid_data ON gestao_tempo_bloqueios (usuario_id, data);

CREATE TABLE IF NOT EXISTS gestao_tempo_config_notif (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER UNIQUE NOT NULL,
    notif_compromissos BOOLEAN DEFAULT TRUE,
    notif_rotinas BOOLEAN DEFAULT TRUE,
    notif_foco BOOLEAN DEFAULT TRUE,
    notif_sugestoes BOOLEAN DEFAULT TRUE,
    minutos_antes INTEGER DEFAULT 15,
    canal_push BOOLEAN DEFAULT TRUE,
    canal_whatsapp BOOLEAN DEFAULT FALSE,
    canal_email BOOLEAN DEFAULT FALSE,
    canal_ligacao BOOLEAN DEFAULT FALSE,
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS gestao_tempo_notificacoes (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    tipo TEXT,
    titulo TEXT,
    mensagem TEXT,
    enviado BOOLEAN DEFAULT FALSE,
    lido BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_gt_notif_uid ON gestao_tempo_notificacoes (usuario_id, criado_em DESC);
