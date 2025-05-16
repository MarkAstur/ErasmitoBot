import os
import discord
from discord.ext import commands
from db import actualizar_mensajes, actualizar_reacciones
from logros import revisar_logros

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def asignar_logro(user, logro, bot):
    import db
    db.registrar_logro(user.id, logro)

    canal = bot.get_channel(LOGROS_CHANNEL_ID)
    if canal:
        embed = discord.Embed(
            title="🏆 ¡Nuevo logro desbloqueado!",
            description=f"**{user.display_name}** ha desbloqueado:\n**{logro}**",
            color=discord.Color.orange()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        await canal.send(embed=embed)

@bot.command(name="resetlogros")
@commands.has_permissions(administrator=True)
async def reset_logros(ctx):
    import db
    db.resetear_todos_los_logros()
    await ctx.send("✅ Todos los logros han sido reseteados.")


#LOGROS_CHANNEL_ID = 1372577946501644450

@bot.event
async def on_ready():
    print(f"Conectado como {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    actualizar_mensajes(user_id)
    nuevos = revisar_logros(user_id)
    if nuevos:
        await message.channel.send(f"🎖️ {message.author.mention} ha desbloqueado: {', '.join(nuevos)}")

    await bot.process_commands(message)

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    actualizar_reacciones(user.id)
    nuevos = revisar_logros(user.id)
    if nuevos:
        await reaction.message.channel.send(f"🎖️ {user.mention} ha desbloqueado: {', '.join(nuevos)}")

@bot.command()
async def logros(ctx):
    from db import obtener_datos
    datos = obtener_datos(ctx.author.id)
    if datos and datos[3]:
        await ctx.send(f"🏆 {ctx.author.mention}, tus logros: {datos[3]}")
    else:
        await ctx.send("😢 Aún no has desbloqueado ningún logro.")

LOGROS_CHANNEL_ID = int(os.getenv("LOGROS_CHANNEL_ID"))

bot.run(os.getenv("DISCORD_TOKEN"))
