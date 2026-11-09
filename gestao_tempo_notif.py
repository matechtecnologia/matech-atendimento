# ============================================
# M.A Tech - Envio de Notificacoes do Tempo
# ============================================
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date, datetime, timedelta


def _conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def _agora():
    return datetime.now()


def _pode_notificar(cur, uid, tipo):
    """Verifica config do usuario: notif_<tipo> ativada?"""
    cur.execute("SELECT * FROM gestao_tempo_config_notif WHERE usuario_id=%s", (uid,))
    cfg = cur.fetchone()
    if not cfg:
        return True, 15, True
    campo = {
        "compromisso": "notif_compromissos",
        "rotina": "notif_rotinas",
        "foco": "notif_foco",
        "sugestao": "notif_sugestoes",
    }.get(tipo)
    if campo and not cfg.get(campo):
        return False, cfg.get("minutos_antes", 15), cfg.get("canal_push", True)
    return True, cfg.get("minutos_antes", 15), cfg.get("canal_push", True)


def _em_bloqueio_foco(cur, uid, agora):
    """Se o momento atual esta dentro de um bloqueio de foco, retorna o titulo do bloqueio."""
    hoje = agora.date()
    hora = agora.time()
    cur.execute("""
        SELECT titulo FROM gestao_tempo_bloqueios
         WHERE usuario_id=%s AND data=%s
           AND hora_inicio <= %s AND hora_fim >= %s
         LIMIT 1
    """, (uid, hoje, hora, hora))
    r = cur.fetchone()
    return r["titulo"] if r else None


def _ja_enviada(cur, uid, tipo, chave):
    """Evita duplicata: mesma chave (ex: 'compromisso:42:15') nao envia 2x."""
    cur.execute("""
        SELECT id FROM gestao_tempo_notificacoes
         WHERE usuario_id=%s AND tipo=%s AND mensagem LIKE %s
         LIMIT 1
    """, (uid, tipo, f"%{chave}%"))
    return cur.fetchone() is not None


def _canais_ativos(cfg):
    if not cfg:
        return ["push"]
    canais = []
    if cfg.get("canal_push"): canais.append("push")
    if cfg.get("canal_whatsapp"): canais.append("whatsapp")
    if cfg.get("canal_email"): canais.append("email")
    if cfg.get("canal_ligacao"): canais.append("ligacao")
    return canais or ["push"]


def _enviar_externo(canal, uid, titulo, mensagem):
    """
    Stub de envio externo. Por enquanto, so registra.
    Quando tiver credenciais, integra aqui (Twilio, SMTP, etc).
    """
    # TODO: integrar WhatsApp/Email quando tiver credenciais
    return True


def verificar_e_enviar():
    """
    Roda a cada minuto (via cron). Olha compromissos e rotinas proximos,
    respeita config + bloqueio de foco, e cria notificacoes.
    """
    agora = _agora()
    criadas = 0
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            # 1) COMPROMISSOS proximos (proximos 90 min)
            horizonte = agora + timedelta(minutes=90)
            cur.execute("""
                SELECT * FROM gestao_tempo_compromissos
                 WHERE concluido=FALSE
                   AND data BETWEEN %s AND %s
                   AND hora_inicio IS NOT NULL
            """, (agora.date(), horizonte.date()))
            comps = cur.fetchall()

            for c in comps:
                uid = c["usuario_id"]
                pode, min_antes, push = _pode_notificar(cur, uid, "compromisso")
                if not pode:
                    continue
                try:
                    dt_comp = datetime.combine(c["data"], c["hora_inicio"])
                except Exception:
                    continue
                delta = (dt_comp - agora).total_seconds() / 60.0
                if delta < 0 or delta > min_antes:
                    continue
                # respeita bloqueio de foco
                if _em_bloqueio_foco(cur, uid, agora):
                    continue
                chave = f"compromisso:{c['id']}:{min_antes}"
                if _ja_enviada(cur, uid, "compromisso", chave):
                    continue
                cfg = None
                cur.execute("SELECT * FROM gestao_tempo_config_notif WHERE usuario_id=%s", (uid,))
                cfg = cur.fetchone()
                canais = _canais_ativos(cfg)
                msg = f"Em {min_antes} min: {c['titulo']} as {c['hora_inicio']}. {chave}"
                cur.execute("""
                    INSERT INTO gestao_tempo_notificacoes (usuario_id, tipo, titulo, mensagem, enviado)
                    VALUES (%s, %s, %s, %s, FALSE)
                """, (uid, "compromisso", c["titulo"], msg))
                criadas += 1
                for canal in canais:
                    try: _enviar_externo(canal, uid, c["titulo"], msg)
                    except Exception: pass

            # 2) ROTINAS de hoje, comecando nos proximos 90 min
            hoje = agora.date()
            dia_semana = (hoje.weekday() + 1) % 7  # Python weekday: seg=0 -> nosso: dom=0
            cur.execute("""
                SELECT * FROM gestao_tempo_rotinas
                 WHERE ativo=TRUE AND dia_semana=%s AND hora_inicio IS NOT NULL
            """, (dia_semana,))
            rotinas = cur.fetchall()

            for r in rotinas:
                uid = r["usuario_id"]
                pode, min_antes, push = _pode_notificar(cur, uid, "rotina")
                if not pode:
                    continue
                try:
                    dt_rot = datetime.combine(hoje, r["hora_inicio"])
                except Exception:
                    continue
                delta = (dt_rot - agora).total_seconds() / 60.0
                if delta < 0 or delta > min_antes:
                    continue
                if _em_bloqueio_foco(cur, uid, agora):
                    continue
                chave = f"rotina:{r['id']}:{hoje.isoformat()}"
                if _ja_enviada(cur, uid, "rotina", chave):
                    continue
                msg = f"Rotina: {r['titulo']} as {r['hora_inicio']}. {chave}"
                cur.execute("""
                    INSERT INTO gestao_tempo_notificacoes (usuario_id, tipo, titulo, mensagem, enviado)
                    VALUES (%s, %s, %s, %s, FALSE)
                """, (uid, "rotina", r["titulo"], msg))
                criadas += 1

            conn.commit()
    return {"ok": True, "criadas": criadas, "momento": agora.isoformat()}
