import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from colorama import init, Fore
import os
import sys
import asyncio

# Inicializa colorama para texto en colores
init(autoreset=True)
load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="$", intents=intents)

async def load_extensions():
    cogs_to_load = [
        "cogs.db_operations",
        "cogs.admin_commands",
        "cogs.ticket_system",
        # "cogs.creador",  # Comentamos esto temporalmente
    ]
    for cog in cogs_to_load:
        try:
            await bot.load_extension(cog)
            print(Fore.GREEN + f"✅ Cargada extensión: {cog}")
        except commands.ExtensionError as e:
            print(Fore.RED + f"❌ Error al cargar {cog}: {e}")

@bot.event
async def on_ready():
    print(Fore.GREEN + f"✅ Bot conectado como {bot.user.name}#{bot.user.discriminator}")
    await load_extensions()
    try:
        await bot.load_extension("cogs.creador")
        print(Fore.GREEN + "✅ Cargada extensión: cogs.creador (carga directa)")
    except commands.ExtensionError as e:
        print(Fore.RED + f"❌ Error al cargar cogs.creador (carga directa): {e}")

    try:
        synced = await bot.tree.sync()
        print(Fore.YELLOW + f"Comandos de aplicación sincronizados globalmente: {len(synced)}")
    except Exception as e:
        print(Fore.RED + f"❌ Error al sincronizar comandos de aplicación: {e}")

async def main():
    async with bot:
        await bot.start(BOT_TOKEN)

if __name__ == "__main__":
    if BOT_TOKEN:
        asyncio.run(main())
    else:
        print(Fore.RED + "❌ Error: BOT_TOKEN no está definido en el archivo .env")