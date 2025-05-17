from db import iniciar_db
iniciar_db()
import discord
from discord.ext import commands
import os
from db import incrementar_mensajes, actualizar_reacciones, revisar_logros
from logros import asignar_logro

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

LOGROS_CHANNEL_ID = int(os.getenv("LOGROS_CHANNEL_ID"))

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    total = incrementar_mensajes(message.author.id)
    nuevos = revisar_logros(message.author.id)

    if 100 in total and "Enviado 100 mensajes" in nuevos:
        await asignar_logro(message.author, "Enviado 100 mensajes", bot)

    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    user = guild.get_member(payload.user_id)

    if user is None or user.bot:
        return

    actualizar_reacciones(user.id)
    nuevos = revisar_logros(user.id)

    if nuevos:
        channel = bot.get_channel(payload.channel_id)
        if channel:
            await channel.send(f"🎖️ {user.mention} ha desbloqueado: {', '.join(nuevos)}")

@bot.command(name="resetlogros")
@commands.has_permissions(administrator=True)
async def reset_logros(ctx):
    from db import resetear_todos_los_logros
    resetear_todos_los_logros()
    await ctx.send("🔄 Todos los logros han sido reiniciados.")

@bot.command(name="resetusuario")
@commands.has_permissions(administrator=True)
async def reset_usuario(ctx, miembro: discord.Member):
    from db import resetear_logros_usuario
    resetear_logros_usuario(miembro.id)
    await ctx.send(f"🔄 Logros reseteados para {miembro.display_name}.")

bot.run(os.getenv("DISCORD_TOKEN"))
