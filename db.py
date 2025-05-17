import sqlite3

def iniciar_db():
    conn = sqlite3.connect("logros.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            user_id INTEGER PRIMARY KEY,
            mensajes INTEGER DEFAULT 0,
            reacciones INTEGER DEFAULT 0
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS logros (
            user_id INTEGER,
            logro TEXT,
            PRIMARY KEY (user_id, logro)
        )
    """)
    conn.commit()
    conn.close()

def incrementar_mensajes(user_id):
    conn = sqlite3.connect("logros.db")
    c = conn.cursor()
    c.execute("SELECT mensajes FROM usuarios WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if row:
        nuevos = row[0] + 1
        c.execute("UPDATE usuarios SET mensajes = ? WHERE user_id = ?", (nuevos, user_id))
    else:
        nuevos = 1
        c.execute("INSERT INTO usuarios (user_id, mensajes) VALUES (?, ?)", (user_id, nuevos))
    conn.commit()
    conn.close()

def actualizar_reacciones(user_id):
    conn = sqlite3.connect("logros.db")
    c = conn.cursor()
    c.execute("SELECT reacciones FROM usuarios WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if row:
        nuevos = row[0] + 1
        c.execute("UPDATE usuarios SET reacciones = ? WHERE user_id = ?", (nuevos, user_id))
    else:
        nuevos = 1
        c.execute("INSERT INTO usuarios (user_id, reacciones) VALUES (?, ?)", (user_id, nuevos))
    conn.commit()
    conn.close()

def resetear_todos_los_logros():
    conn = sqlite3.connect("logros.db")
    c = conn.cursor()
    c.execute("DELETE FROM logros")
    conn.commit()
    conn.close()

def resetear_logros_usuario(user_id):
    conn = sqlite3.connect("logros.db")
    c = conn.cursor()
    c.execute("DELETE FROM logros WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
