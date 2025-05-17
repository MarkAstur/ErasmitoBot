import sqlite3
import discord
import os

LOGROS = [
    #LOGROS MENSAJES
    {
        "nombre": "Enviado 1 mensaje",
        "condicion": lambda datos: datos["mensajes"] >= 1
    },
    {
        "nombre": "Enviado 100 mensajes",
        "condicion": lambda datos: datos["mensajes"] >= 100
    },
    {
        "nombre": "Enviado 500 mensajes",
        "condicion": lambda datos: datos["mensajes"] >= 500
    },
    
    #LOGROS REACCIONES
    {
        "nombre": "Primera reacción",
        "condicion": lambda datos: datos["reacciones"] >= 1
    },
    {
        "nombre": "10 reacciones dadas",
        "condicion": lambda datos: datos["reacciones"] >= 10
    },
    
    #LOGROS TIEMPO EN SERVIDOR
    {"nombre": "Arena en los Zapatos - Acabas de llegar a DuneVerso", 
     "condicion": lambda stats: stats.get("dias_en_servidor", 0) >= 1},
]

def obtener_datos_usuario(user_id):
    conn = sqlite3.connect("logros.db")
    c = conn.cursor()
    c.execute("SELECT mensajes, reacciones FROM usuarios WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"mensajes": row[0], "reacciones": row[1]}
    else:
        return {"mensajes": 0, "reacciones": 0}

def logros_ya_obtenidos(user_id):
    conn = sqlite3.connect("logros.db")
    c = conn.cursor()
    c.execute("SELECT logro FROM logros WHERE user_id = ?", (user_id,))
    existentes = set(row[0] for row in c.fetchall())
    conn.close()
    return existentes

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
                    description=f"**{user.display_name}** ha conseguido el logro:\n**{logro}**",
                    color=discord.Color.gold()
                )
                embed.set_thumbnail(url=user.display_avatar.url)
                await canal.send(embed=embed)

    return nuevos
