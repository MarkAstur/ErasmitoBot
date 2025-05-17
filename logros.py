import sqlite3
import discord
import os

# LISTADO DE LOGROS
LOGROS = [
    # LOGROS MENSAJES
    {
        "nombre": "Enviado 1 mensaje",
        "condicion": lambda datos: datos.get("mensajes", 0) >= 1
    },
    {
        "nombre": "Enviado 100 mensajes",
        "condicion": lambda datos: datos.get("mensajes", 0) >= 100
    },
    {
        "nombre": "Enviado 500 mensajes",
        "condicion": lambda datos: datos.get("mensajes", 0) >= 500
    },
    
    # LOGROS REACCIONES
    {
        "nombre": "Primera reacción",
        "condicion": lambda datos: datos.get("reacciones", 0) >= 1
    },
    {
        "nombre": "10 reacciones dadas",
        "condicion": lambda datos: datos.get("reacciones", 0) >= 10
    },
    
    # LOGROS TIEMPO EN SERVIDOR
    {
        "nombre": "Arena en los Zapatos - Acabas de llegar a DuneVerso",
        "condicion": lambda datos: datos.get("dias_en_servidor", 0) >= 0
    },

    # LOGROS MENCIONES
    {
        "nombre": "Novato de la Voz - Mencionas a un Usuario",
        "condicion": lambda datos: datos.get("menciones", 0) >= 1
    },
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

async def asignar_logro(user, message, bot):
    user_id = user.id
    datos = obtener_datos_usuario(user_id)
    existentes = logros_ya_obtenidos(user_id)
    nuevos = []

    # Calcular días en servidor
    joined_at = None
    if hasattr(user, "joined_at") and user.joined_at:
        joined_at = user.joined_at
    elif hasattr(user, "member") and user.member and user.member.joined_at:
        joined_at = user.member.joined_at
    
    if joined_at:
        dias_en_servidor = (discord.utils.utcnow() - joined_at).days
    else:
        dias_en_servidor = 0

    datos["dias_en_servidor"] = dias_en_servidor

    # Para el logro de menciones, verificamos si el mensaje menciona a alguien
    if message and message.mentions:
        datos["menciones"] = len(message.mentions)
    else:
        datos["menciones"] = 0

    for logro in LOGROS:
        nombre = logro["nombre"]
        if nombre not in existentes and logro["condicion"](datos):
            registrar_logro(user_id, nombre)
            nuevos.append(nombre)

    if nuevos:
        canal_id = os.getenv("LOGROS_CHANNEL_ID")
        if canal_id:
            canal = bot.get_channel(int(canal_id))
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
