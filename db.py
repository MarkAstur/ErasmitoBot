
import sqlite3

def agregar_columna_voz_si_no_existe():
    conn = sqlite3.connect("logros.db")
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE usuarios ADD COLUMN voz INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Ya existe
    conn.commit()
    conn.close()

def iniciar_db():
    conn = sqlite3.connect("logros.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            user_id INTEGER PRIMARY KEY,
            mensajes INTEGER DEFAULT 0,
            reacciones INTEGER DEFAULT 0,
            tiempo_total INTEGER DEFAULT 0
            -- voz se agregará aparte
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS estadisticas (
            usuario_id INTEGER PRIMARY KEY,
            menciones INTEGER DEFAULT 0
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

    # ✅ Ahora sí, la tabla 'usuarios' ya existe
    agregar_columna_voz_si_no_existe()

def incrementar_mensajes(user_id):
    conn = sqlite3.connect("logros.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO usuarios (user_id, mensajes) VALUES (?, 0)", (user_id,))
    c.execute("UPDATE usuarios SET mensajes = mensajes + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def actualizar_reacciones(user_id):
    conn = sqlite3.connect("logros.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO usuarios (user_id, reacciones) VALUES (?, 0)", (user_id,))
    c.execute("UPDATE usuarios SET reacciones = reacciones + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def incrementar_menciones(user_id):
    conn = sqlite3.connect("logros.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO estadisticas (usuario_id, menciones) VALUES (?, 0)", (user_id,))
    c.execute("UPDATE estadisticas SET menciones = menciones + 1 WHERE usuario_id = ?", (user_id,))
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

def resetear_todas_las_estadisticas():
    conn = sqlite3.connect("logros.db")
    c = conn.cursor()
    c.execute("DELETE FROM usuarios")
    c.execute("DELETE FROM estadisticas")
    conn.commit()
    conn.close()

def resetear_estadisticas_usuario(user_id):
    conn = sqlite3.connect("logros.db")
    c = conn.cursor()
    c.execute("DELETE FROM usuarios WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM estadisticas WHERE usuario_id = ?", (user_id,))
    conn.commit()
    conn.close()
