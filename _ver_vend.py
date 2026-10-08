import app
c = app.get_conn()
cur = c.cursor()

# Ver o vendedor do usuario admin (id=1)
cur.execute("""SELECT v.id, v.plano, u.tipo, u.email
               FROM vendedores v 
               JOIN usuarios u ON u.id = v.usuario_id 
               WHERE u.email = 'matechtecnologia01@gmail.com'""")
for r in cur.fetchall():
    print(r)

cur.close()
app.close_conn(c)
