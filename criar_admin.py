import sqlite3
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def criar_admin():
    conn = sqlite3.connect("dados.db")
    cursor = conn.cursor()

    email = "matechtecnologia01@gmail.com"
    senha = "M@techtechnologia12997291583"
    senha_hash = pwd_context.hash(senha)

    try:
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha, tipo)
            VALUES (?, ?, ?, ?)
        """, ("Admin M.A Tech", email, senha_hash, "admin"))
        conn.commit()
        print(f"Admin criado: {email}")
    except sqlite3.IntegrityError:
        print(f"Admin ja existe: {email}")
    finally:
        conn.close()

if __name__ == "__main__":
    criar_admin()