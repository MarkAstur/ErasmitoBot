import discord
from discord.ext import commands
import os
from db import incrementar_mensajes, actualizar_reacciones
from logros import asignar_logro

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    incrementar_mensajes(message.author.id)
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
