
import sqlite3
import discord
import os

LOGROS = [
    #LOGROS MENSAJES
    {"nombre": "Pequeño Hacedor Recien Nacido - Enviado tu primer Mensaje", "condicion": lambda d: d["mensajes"] >= 1, "imagen": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/1689500/c3302e073a99fc5d38642be124c5364dcd8db2a5.jpg"},
    {"nombre": "Trucha de Arena - Enviado 100 mensajes", "condicion": lambda d: d["mensajes"] >= 100, "imagen": "user.display_avatar.url"},
    {"nombre": "Gusano de Arena Jóven - Enviado 500 mensajes", "condicion": lambda d: d["mensajes"] >= 500, "imagen": "user.display_avatar.url"},
    {"nombre": "Gusano de Arena Adulto - Enviado 1000 mensajes", "condicion": lambda d: d["mensajes"] >= 1000, "imagen": "user.display_avatar.url"},
    {"nombre": "Shai-Hulud - Enviado 1500 mensajes", "condicion": lambda d: d["mensajes"] >= 1500, "imagen": "user.display_avatar.url"},
    {"nombre": "Frank Herbert Cabalgando a Shai-Hulud - Enviado 5000 mensajes", "condicion": lambda d: d["mensajes"] >= 5000, "imagen": "user.display_avatar.url"},
    #LOGROS REACCIONES
    {"nombre": "Mentat Desmemoriado - Primera reacción", "condicion": lambda d: d["reacciones"] >= 1, "imagen": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/1689500/4117a9df617f48023467e59318ac6cbb37c68dbe.jpg"},
    {"nombre": "Hermana Bene Gesserit - 10 reacciones dadas", "condicion": lambda d: d["reacciones"] >= 10, "imagen": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/1689500/4117a9df617f48023467e59318ac6cbb37c68dbe.jpg"},
    {"nombre": "Otras Memorias - 25 reacciones dadas", "condicion": lambda d: d["reacciones"] >= 25, "imagen": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/1689500/4117a9df617f48023467e59318ac6cbb37c68dbe.jpg"},
    {"nombre": "Agua de la Vida - 50 reacciones dadas", "condicion": lambda d: d["reacciones"] >= 50, "imagen": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/1689500/4117a9df617f48023467e59318ac6cbb37c68dbe.jpg"},
    #LOGROS TIEMPO
    {"nombre": "Arena en los Zapatos - Acabas de llegar a DuneVerso", "condicion": lambda d: d.get("dias_en_servidor", 0) >= 0, "imagen": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/1689500/43a74dfebf1567ec5408dc15dd2e2f94153fda85.jpg"},
    #LOGROS MENCIONES
    {"nombre": "Novato de la Voz - Mencionas a un Usuario", "condicion": lambda d: d.get("menciones", 0) >= 1, "imagen": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/1689500/05f9c48a93e12754a31d03a1f1f52a4cbc254eb1.jpg"},
    #LOGROS ENTRAR CANALES
    {"nombre": "Uso de la Voz - Primera vez que entras en un canal de Voz", "condicion": lambda d: d.get("voz", 0) >= 1, "imagen": "https://i.ibb.co/zHV0wLTq/00.png"},
    #LOGROS POR OBTENER UN ROL
    {"primer_rol": {"nombre": "Has sido elegido", "descripcion": "Recibiste tu primer rol en el servidor.", "imagen": "url_o_ruta_de_la_imagen.png"},
}
]

def obtener_datos_usuario(user_id):
    conn = sqlite3.connect("logros.db")
    c = conn.cursor()
    c.execute("SELECT mensajes, reacciones, voz FROM usuarios WHERE user_id = ?", (user_id,))
    row1 = c.fetchone()
    c.execute("SELECT menciones FROM estadisticas WHERE usuario_id = ?", (user_id,))
    row2 = c.fetchone()
    conn.close()

    return {
        "mensajes": row1[0] if row1 else 0,
        "reacciones": row1[1] if row1 else 0,
        "voz": row1[2] if row1 else 0,
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
