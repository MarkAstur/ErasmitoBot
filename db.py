import sqlite3

conn = sqlite3.connect("logros.db")
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    user_id INTEGER PRIMARY KEY,
    mensajes INTEGER DEFAULT 0,
    reacciones INTEGER DEFAULT 0,
    tiempo_ingreso TEXT,
    logros TEXT DEFAULT ''
)
''')

conn.commit()

def registrar_usuario(user_id):
    c.execute("SELECT 1 FROM usuarios WHERE user_id = ?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO usuarios (user_id, tiempo_ingreso) VALUES (?, datetime('now'))", (user_id,))
        conn.commit()

def actualizar_mensajes(user_id):
    registrar_usuario(user_id)
    c.execute("UPDATE usuarios SET mensajes = mensajes + 1 WHERE user_id = ?", (user_id,))
    conn.commit()

def actualizar_reacciones(user_id):
    registrar_usuario(user_id)
    c.execute("UPDATE usuarios SET reacciones = reacciones + 1 WHERE user_id = ?", (user_id,))
    conn.commit()

def obtener_datos(user_id):
    c.execute("SELECT mensajes, reacciones, tiempo_ingreso, logros FROM usuarios WHERE user_id = ?", (user_id,))
    return c.fetchone()

def guardar_logros(user_id, nuevos_logros):
    _, _, _, logros_actuales = obtener_datos(user_id)
    todos = logros_actuales.split(",") if logros_actuales else []
    nuevos = [l for l in nuevos_logros if l not in todos]
    if nuevos:
        resultado = ",".join(todos + nuevos)
        c.execute("UPDATE usuarios SET logros = ? WHERE user_id = ?", (resultado, user_id))
        conn.commit()
    return nuevos