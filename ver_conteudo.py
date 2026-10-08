import app
c = app.get_conn()
cur = c.cursor()

print("=== PRODUCTS ===")
cur.execute("SELECT id, nome, status FROM products ORDER BY id")
for r in cur.fetchall():
    print(r)

print()
print("=== PROJECTS ===")
cur.execute("SELECT id, nome, status FROM projects ORDER BY id")
for r in cur.fetchall():
    print(r)

print()
print("=== GOALS ===")
cur.execute("SELECT id, titulo FROM goals ORDER BY id")
for r in cur.fetchall():
    print(r)

print()
print("=== TASKS (primeiras 30) ===")
cur.execute("SELECT id, titulo, status FROM tasks ORDER BY id LIMIT 30")
for r in cur.fetchall():
    print(r)

print()
print("=== BLOCKERS ===")
cur.execute("SELECT id, titulo, status FROM blockers ORDER BY id")
for r in cur.fetchall():
    print(r)

print()
print("=== METRICS ===")
cur.execute("SELECT id, nome FROM metrics ORDER BY id")
for r in cur.fetchall():
    print(r)

cur.close()
app.close_conn(c)
