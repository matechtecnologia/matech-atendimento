import app
c = app.get_conn()
cur = c.cursor()
cur.execute("DELETE FROM blockers WHERE titulo='Bug de login em /plano'")
c.commit()
print("Blocker falso removido")
cur.close()
app.close_conn(c)
