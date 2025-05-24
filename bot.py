import sqlite3
import discord
from discord.ext import commands
import os
from db import incrementar_mensajes, actualizar_reacciones, incrementar_menciones, iniciar_db
from logros import asignar_logro

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_member_update(before, after):
    # Verifica si se ha añadido un nuevo rol
    nuevos_roles = [role for role in after.roles if role not in before.roles]
    
    for rol in nuevos_roles:
        if rol.name == "Dios Emperador":  # Reemplaza con el nombre exacto del rol que activa el logro
            # Asigna el logro
            await asignar_logro(after, "primer_rol", bot)

@bot.event
async def on_ready():
    iniciar_db()
    print(f"✅ Bot conectado como {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        # El usuario acaba de entrar a un canal de voz
        user_id = member.id

        conn = sqlite3.connect("logros.db")
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO usuarios (user_id, voz) VALUES (?, 0)", (user_id,))
        c.execute("SELECT voz FROM usuarios WHERE user_id = ?", (user_id,))
        ya_entro = c.fetchone()[0]
        if ya_entro == 0:
            c.execute("UPDATE usuarios SET voz = 1 WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()

            # Ahora asigna el logro si corresponde
            await asignar_logro(member, None, bot)
        else:
            conn.close()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    incrementar_mensajes(message.author.id)

    if message.mentions:
        incrementar_menciones(message.author.id)

    await asignar_logro(message.author, None, bot)
    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    user = guild.get_member(payload.user_id)

    if user and not user.bot:
        actualizar_reacciones(user.id)
        await asignar_logro(user, None, bot)

@bot.command(name="resetlogros")
@commands.has_permissions(administrator=True)
async def reset_logros(ctx):
    from db import resetear_todos_los_logros, resetear_todas_las_estadisticas
    resetear_todos_los_logros()
    resetear_todas_las_estadisticas()
    await ctx.send("🔄 Todos los logros y estadísticas han sido reiniciados.")

@bot.command(name="resetusuario")
@commands.has_permissions(administrator=True)
async def reset_usuario(ctx, miembro: discord.Member):
    from db import resetear_logros_usuario, resetear_estadisticas_usuario
    resetear_logros_usuario(miembro.id)
    resetear_estadisticas_usuario(miembro.id)
    await ctx.send(f"🔄 Logros y estadísticas reseteadas para {miembro.display_name}.")

@bot.command(name="verlogros")
async def ver_logros(ctx, miembro: discord.Member = None):
    miembro = miembro or ctx.author
    conn = sqlite3.connect("logros.db")
    c = conn.cursor()
    c.execute("SELECT logro FROM logros WHERE user_id = ?", (miembro.id,))
    logros = [row[0] for row in c.fetchall()]
    conn.close()

    if logros:
        descripcion = "\n".join(f"🏆 {logro}" for logro in logros)
    else:
        descripcion = "Este usuario aún no ha desbloqueado logros."

    embed = discord.Embed(
        title=f"Logros de {miembro.display_name}",
        description=descripcion,
        color=discord.Color.blurple()
    )
    embed.set_thumbnail(url=miembro.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="verstats")
async def ver_stats(ctx, miembro: discord.Member = None):
    miembro = miembro or ctx.author
    conn = sqlite3.connect("logros.db")
    c = conn.cursor()
    c.execute("SELECT mensajes, reacciones FROM usuarios WHERE user_id = ?", (miembro.id,))
    usuario = c.fetchone()
    mensajes = usuario[0] if usuario else 0
    reacciones = usuario[1] if usuario else 0

    c.execute("SELECT menciones FROM estadisticas WHERE usuario_id = ?", (miembro.id,))
    estadisticas = c.fetchone()
    menciones = estadisticas[0] if estadisticas else 0
    conn.close()

    embed = discord.Embed(
        title=f"📈 Estadísticas de {miembro.display_name}",
        color=discord.Color.green()
    )
    embed.add_field(name="📨 Mensajes", value=mensajes, inline=True)
    embed.add_field(name="👍 Reacciones dadas", value=reacciones, inline=True)
    embed.add_field(name="📣 Menciones", value=menciones, inline=True)
    embed.set_thumbnail(url=miembro.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="canallogros")
@commands.has_permissions(administrator=True)
async def canallogros(ctx):
    channel_id = os.getenv("LOGROS_CHANNEL_ID")
    canal = bot.get_channel(int(channel_id)) if channel_id else None
    if not canal:
        canal = await ctx.guild.create_text_channel("logros")
        os.environ["LOGROS_CHANNEL_ID"] = str(canal.id)
        await ctx.send(f"✅ Canal de logros creado: {canal.mention}")
    else:
        await ctx.send(f"✅ Canal de logros ya existe: {canal.mention}")

bot.run(os.getenv("DISCORD_TOKEN"))
