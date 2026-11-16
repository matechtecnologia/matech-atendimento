# ============================================
# M.A Tech — Rotas de foto de perfil (Supabase Storage)
# ============================================
import os
import uuid
from fastapi import Request, UploadFile, File, Cookie
from fastapi.responses import JSONResponse, RedirectResponse


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
BUCKET = "avatars"
MAX_BYTES = 2 * 1024 * 1024  # 2 MB
TIPOS_OK = {"image/jpeg", "image/png", "image/webp"}


def _upload_supabase(path: str, conteudo: bytes, content_type: str) -> str:
    import httpx
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise RuntimeError("SUPABASE_URL ou SUPABASE_SERVICE_KEY nao configuradas")
    url = f"{SUPABASE_URL}/storage/v1/object/avatars/{path}"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": content_type,
        "x-upsert": "true",
    }
    resp = httpx.post(url, content=conteudo, headers=headers, timeout=30)
    resp.raise_for_status()
    return f"{SUPABASE_URL}/storage/v1/object/public/avatars/{path}"


def _ext_por_mime(mime: str) -> str:
    return {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}.get(mime, "jpg")


def instalar_foto_rotas(app, templates, ler_sessao, get_conn, close_conn):

    @app.post("/upload-avatar")
    async def upload_avatar(request: Request, arquivo: UploadFile = File(...), usuario_id: str = Cookie(None)):
        if not usuario_id:
            return JSONResponse({"erro": "nao autenticado"}, status_code=401)

        if arquivo.content_type not in TIPOS_OK:
            return JSONResponse({"erro": "tipo invalido. Use JPG, PNG ou WEBP."}, status_code=400)

        conteudo = await arquivo.read()
        if len(conteudo) > MAX_BYTES:
            return JSONResponse({"erro": "arquivo maior que 2 MB"}, status_code=400)
        if len(conteudo) == 0:
            return JSONResponse({"erro": "arquivo vazio"}, status_code=400)

        ext = _ext_por_mime(arquivo.content_type)
        path = f"{usuario_id}.{ext}"

        try:
            url_publica = _upload_supabase(path, conteudo, arquivo.content_type)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JSONResponse({"erro": f"falha no upload: {e}"}, status_code=500)

        # Adiciona cache-buster pra forcar o navegador a baixar a versao nova
        url_final = f"{url_publica}?v={uuid.uuid4().hex[:8]}"

        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("UPDATE usuarios SET foto_url = %s WHERE id = %s", (url_final, usuario_id))
            conn.commit()
            cur.close()
            close_conn(conn)
        except Exception as e:
            return JSONResponse({"erro": f"falha ao salvar no banco: {e}"}, status_code=500)

        return JSONResponse({"ok": True, "foto_url": url_final})

    @app.get("/api/usuario/foto")
    def api_usuario_foto(usuario_id: str = Cookie(None)):
        if not usuario_id:
            return JSONResponse({"foto_url": None})
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT foto_url FROM usuarios WHERE id = %s", (usuario_id,))
            row = cur.fetchone()
            cur.close()
            close_conn(conn)
            return JSONResponse({"foto_url": row[0] if row and row[0] else None})
        except Exception:
            return JSONResponse({"foto_url": None})
