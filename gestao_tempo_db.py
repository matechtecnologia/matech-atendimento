# ============================================
# M.A Tech - DB Gestao Pessoal do Tempo
# ============================================
import os
import psycopg2
from psycopg2.extras import RealDictCursor


def _conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


# ---------- COMPROMISSOS ----------

def salvar_compromisso(uid, titulo, data, hora_inicio=None, hora_fim=None,
                       descricao=None, local=None, categoria=None, prioridade="media"):
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO gestao_tempo_compromissos
                    (usuario_id, titulo, descricao, data, hora_inicio, hora_fim, local, categoria, prioridade)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id
            """, (uid, titulo, descricao, data, hora_inicio, hora_fim, local, categoria, prioridade))
            novo_id = cur.fetchone()["id"]
            conn.commit()
            return novo_id


def editar_compromisso(uid, cid, titulo, data, hora_inicio=None, hora_fim=None,
                       descricao=None, local=None, categoria=None, prioridade="media"):
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE gestao_tempo_compromissos
                   SET titulo=%s, descricao=%s, data=%s, hora_inicio=%s, hora_fim=%s,
                       local=%s, categoria=%s, prioridade=%s
                 WHERE id=%s AND usuario_id=%s
            """, (titulo, descricao, data, hora_inicio, hora_fim, local, categoria, prioridade, cid, uid))
            conn.commit()


def deletar_compromisso(uid, cid):
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM gestao_tempo_compromissos WHERE id=%s AND usuario_id=%s", (cid, uid))
            conn.commit()


def marcar_compromisso_concluido(uid, cid, concluido=True):
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE gestao_tempo_compromissos SET concluido=%s WHERE id=%s AND usuario_id=%s",
                        (concluido, cid, uid))
            conn.commit()


def obter_compromisso(uid, cid):
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM gestao_tempo_compromissos WHERE id=%s AND usuario_id=%s", (cid, uid))
            return cur.fetchone()


def listar_compromissos_dia(uid, dia):
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM gestao_tempo_compromissos
                 WHERE usuario_id=%s AND data=%s
                 ORDER BY hora_inicio NULLS LAST, id
            """, (uid, dia))
            return [dict(r) for r in cur.fetchall()]


def listar_compromissos_semana(uid, data_inicio, data_fim):
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM gestao_tempo_compromissos
                 WHERE usuario_id=%s AND data BETWEEN %s AND %s
                 ORDER BY data, hora_inicio NULLS LAST, id
            """, (uid, data_inicio, data_fim))
            return [dict(r) for r in cur.fetchall()]


# ---------- ROTINAS ----------

def salvar_rotina(uid, titulo, dia_semana, hora_inicio=None, hora_fim=None, categoria=None):
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO gestao_tempo_rotinas
                    (usuario_id, titulo, dia_semana, hora_inicio, hora_fim, categoria)
                VALUES (%s,%s,%s,%s,%s,%s)
                RETURNING id
            """, (uid, titulo, dia_semana, hora_inicio, hora_fim, categoria))
            novo_id = cur.fetchone()["id"]
            conn.commit()
            return novo_id


def listar_rotinas(uid, apenas_ativas=True):
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if apenas_ativas:
                cur.execute("SELECT * FROM gestao_tempo_rotinas WHERE usuario_id=%s AND ativo=TRUE ORDER BY dia_semana, hora_inicio", (uid,))
            else:
                cur.execute("SELECT * FROM gestao_tempo_rotinas WHERE usuario_id=%s ORDER BY dia_semana, hora_inicio", (uid,))
            return [dict(r) for r in cur.fetchall()]


def alternar_rotina(uid, rid, ativo):
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE gestao_tempo_rotinas SET ativo=%s WHERE id=%s AND usuario_id=%s", (ativo, rid, uid))
            conn.commit()


def deletar_rotina(uid, rid):
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM gestao_tempo_rotinas WHERE id=%s AND usuario_id=%s", (rid, uid))
            conn.commit()


# ---------- BLOQUEIO DE FOCO ----------

def bloquear_foco(uid, data, hora_inicio, hora_fim, titulo="Foco"):
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO gestao_tempo_bloqueios (usuario_id, titulo, data, hora_inicio, hora_fim)
                VALUES (%s,%s,%s,%s,%s)
                RETURNING id
            """, (uid, titulo, data, hora_inicio, hora_fim))
            novo_id = cur.fetchone()["id"]
            conn.commit()
            return novo_id


def listar_bloqueios_dia(uid, dia):
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM gestao_tempo_bloqueios WHERE usuario_id=%s AND data=%s ORDER BY hora_inicio", (uid, dia))
            return [dict(r) for r in cur.fetchall()]


def deletar_bloqueio(uid, bid):
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM gestao_tempo_bloqueios WHERE id=%s AND usuario_id=%s", (bid, uid))
            conn.commit()


# ---------- CONFIG NOTIFICACAO ----------

def obter_config_notif(uid):
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO gestao_tempo_config_notif (usuario_id) VALUES (%s)
                ON CONFLICT (usuario_id) DO NOTHING
            """, (uid,))
            conn.commit()
            cur.execute("SELECT * FROM gestao_tempo_config_notif WHERE usuario_id=%s", (uid,))
            return dict(cur.fetchone())


def atualizar_config_notif(uid, dados):
    campos = ["notif_compromissos", "notif_rotinas", "notif_foco", "notif_sugestoes",
              "minutos_antes", "canal_push", "canal_whatsapp", "canal_email", "canal_ligacao"]
    sets = ", ".join(f"{c}=%s" for c in campos)
    valores = [dados.get(c) for c in campos] + [uid]
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"UPDATE gestao_tempo_config_notif SET {sets}, atualizado_em=NOW() WHERE usuario_id=%s", valores)
            conn.commit()


# ---------- NOTIFICACOES ----------

def registrar_notificacao(uid, tipo, titulo, mensagem, enviado=False):
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO gestao_tempo_notificacoes (usuario_id, tipo, titulo, mensagem, enviado)
                VALUES (%s,%s,%s,%s,%s)
                RETURNING id
            """, (uid, tipo, titulo, mensagem, enviado))
            novo_id = cur.fetchone()["id"]
            conn.commit()
            return novo_id


def listar_notificacoes(uid, limite=100):
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM gestao_tempo_notificacoes WHERE usuario_id=%s ORDER BY criado_em DESC LIMIT %s", (uid, limite))
            return [dict(r) for r in cur.fetchall()]


def marcar_notificacao_lida(uid, nid):
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE gestao_tempo_notificacoes SET lido=TRUE WHERE id=%s AND usuario_id=%s", (nid, uid))
            conn.commit()
