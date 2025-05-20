
import sqlite3
import discord
import os

LOGROS = [
    #LOGROS MENSAJES
    {"nombre": "Trucha de Arena Recién Nacida - Enviado tu primer Mensaje", "condicion": lambda d: d["mensajes"] >= 1, "imagen": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/1689500/c3302e073a99fc5d38642be124c5364dcd8db2a5.jpg"},
    {"nombre": "Enviado 100 mensajes", "condicion": lambda d: d["mensajes"] >= 100, "imagen": "user.display_avatar.url"},
    {"nombre": "Enviado 500 mensajes", "condicion": lambda d: d["mensajes"] >= 500, "imagen": "user.display_avatar.url"},
    #LOGROS REACCIONES
    {"nombre": "Mentat Desmemoriad@ - Primera reacción", "condicion": lambda d: d["reacciones"] >= 1, "imagen": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/1689500/4117a9df617f48023467e59318ac6cbb37c68dbe.jpg"},
    {"nombre": "10 reacciones dadas", "condicion": lambda d: d["reacciones"] >= 10, "imagen": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/1689500/4117a9df617f48023467e59318ac6cbb37c68dbe.jpg"},
    #LOGROS TIEMPO
    {"nombre": "Arena en los Zapatos - Acabas de llegar a DuneVerso", "condicion": lambda d: d.get("dias_en_servidor", 0) >= 0, "imagen": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/1689500/43a74dfebf1567ec5408dc15dd2e2f94153fda85.jpg"},
    #LOGROS MENCIONES
    {"nombre": "Novato de la Voz - Mencionas a un Usuario", "condicion": lambda d: d.get("menciones", 0) >= 1, "imagen": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/1689500/05f9c48a93e12754a31d03a1f1f52a4cbc254eb1.jpg"},
    #LOGROS ENTRAR CANALES
    {"nombre": "Uso de la Voz - Primera vez que entras en un canal de Voz", "condicion": lambda d: d.get("voz", 0) >= 1, "imagen": "https://static.wikia.nocookie.net/dune/images/8/8c/51oT6J972oL._SY445_-1.jpg"},
}

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
                logro_data = next((l for l in LOGROS if l["nombre"] == logro), None)
                imagen_url = logro_data.get("imagen") if logro_data else None

                embed = discord.Embed(
                title="🏆 ¡Nuevo logro desbloqueado!",
                description=f"**{user.display_name}** ha conseguido el logro:\n**{logro}**",
                color=discord.Color.gold()
    )

    if imagen_url:
        embed.set_thumbnail(url=imagen_url)
    else:
        embed.set_thumbnail(url=user.display_avatar.url)

    await canal.send(embed=embed)
