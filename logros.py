
import sqlite3
import discord
import os

LOGROS = [
    {"nombre": "Enviado 1 mensaje", "condicion": lambda d: d["mensajes"] >= 1},
    {"nombre": "Enviado 100 mensajes", "condicion": lambda d: d["mensajes"] >= 100},
    {"nombre": "Enviado 500 mensajes", "condicion": lambda d: d["mensajes"] >= 500},
    {"nombre": "Primera reacción", "condicion": lambda d: d["reacciones"] >= 1},
    {"nombre": "10 reacciones dadas", "condicion": lambda d: d["reacciones"] >= 10},
    {"nombre": "Arena en los Zapatos - Acabas de llegar a DuneVerso", "condicion": lambda d: d.get("dias_en_servidor", 0) >= 0},
    {"nombre": "Novato de la Voz - Mencionas a un Usuario", "condicion": lambda d: d.get("menciones", 0) >= 1},
]

def obtener_datos_usuario(user_id):
    conn = sqlite3.connect("logros.db")
    c = conn.cursor()
    c.execute("SELECT mensajes, reacciones FROM usuarios WHERE user_id = ?", (user_id,))
    row1 = c.fetchone()
    c.execute("SELECT menciones FROM estadisticas WHERE usuario_id = ?", (user_id,))
    row2 = c.fetchone()
    conn.close()

    return {
        "mensajes": row1[0] if row1 else 0,
        "reacciones": row1[1] if row1 else 0,
        "menciones": row2[0] if row2 else 0
    }

def logros_ya_obtenidos(user_id):
    conn = sqlite3.connect("logros.db")
    c = conn.cursor()
    c.execute("SELECT logro FROM logros WHERE user_id = ?", (user_id,))
    res = set(row[0] for row in c.fetchall())
    conn.close()
    return res

def registrar_logro(user_id, logro):
    conn = sqlite3.connect("logros.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO logros (user_id, logro) VALUES (?, ?)", (user_id, logro))
    conn.commit()
    conn.close()

async def asignar_logro(user, _, bot):
    user_id = user.id
    datos = obtener_datos_usuario(user_id)
    existentes = logros_ya_obtenidos(user_id)
    nuevos = []

    miembro = user if hasattr(user, "joined_at") else None
    dias_en_servidor = (discord.utils.utcnow() - miembro.joined_at).days if miembro and miembro.joined_at else 0
    datos["dias_en_servidor"] = dias_en_servidor

    for logro in LOGROS:
        nombre = logro["nombre"]
        if nombre not in existentes and logro["condicion"](datos):
            registrar_logro(user_id, nombre)
            nuevos.append(nombre)

    if nuevos:
        canal = bot.get_channel(int(os.getenv("LOGROS_CHANNEL_ID")))
        if canal:
            for logro in nuevos:
                embed = discord.Embed(
                    title="🏆 ¡Nuevo logro desbloqueado!",
                    description=f"**{user.display_name}** ha conseguido el logro:
**{logro}**",
                    color=discord.Color.gold()
                )
                embed.set_thumbnail(url=user.display_avatar.url)
                await canal.send(embed=embed)
