import discord 
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from colorama import init, Fore
from aiohttp import web
import os
import asyncio
from db_operations import DBOperations

# Inicializa colorama y carga variables de entorno
init(autoreset=True)
load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Instancia del bot
bot = commands.Bot(command_prefix="$", intents=intents)

# Variable global para saber el tipo de desconexión
shutdown_type = "manual"  # manual o auto

# ===============================
# 🔌 CARGA DE EXTENSIONES
# ===============================
async def load_extensions(bot):
    cogs_to_load = [
        "db_operations",
        "cogs.ayuda",
        "cogs.admin_commands",
        "cogs.ticket_system",
        "cogs.activity_tracker",
        "cogs.inactivity_checker",
        "cogs.embeds",
        "cogs.automod",
        "cogs.recordatorio",
        "cogs.diversión1",
        "cogs.diversión2",
        "cogs.desahogo",
        "cogs.sorteo",
        "cogs.vc",
        "cogs.moderation.actions",
        "cogs.moderation.info",
        "cogs.moderation.infractions",
        "cogs.moderation.messages",
        "cogs.moderation.modlog",
        "cogs.moderation.report",
        "cogs.moderation.warnings",
        "cogs.creador"
    ]

    for cog in cogs_to_load:
        try:
            await bot.load_extension(cog)
            print(Fore.GREEN + f"✅ Cog cargado: {cog}")
        except Exception as e:
            print(Fore.RED + f"❌ Error cargando {cog}: {e}")

# ===============================
# 🤖 EVENTO AL INICIAR
# ===============================
@bot.event
async def on_ready():
    print(Fore.GREEN + f"✅ Bot conectado como {bot.user.name}#{bot.user.discriminator}")
    print(Fore.CYAN + f"🌐 Conectado a {len(bot.guilds)} servidores")

    try:
        synced = await bot.tree.sync()
        print(Fore.YELLOW + f"🔃 Comandos de aplicación sincronizados: {len(synced)}")
    except Exception as e:
        print(Fore.RED + f"❌ Error al sincronizar comandos: {e}")

# ===============================
# ❌ EVENTO AL DESCONECTARSE
# ===============================
@bot.event
async def on_disconnect():
    if shutdown_type == "auto":
        print(Fore.MAGENTA + "🔌 Bot desconectado automáticamente.")
    else:
        print(Fore.MAGENTA + "🛑 Bot desconectado manualmente.")

# ===============================
# 🛰️ KEEP-ALIVE WEB SERVER
# ===============================
async def handle_ping(request):
    return web.Response(text="✅ Bot activo y en línea.")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 3000)
    await site.start()
    print(Fore.LIGHTBLUE_EX + "🌐 Servidor de keep-alive iniciado en puerto 3000.")

# ===============================
# 🎯 MAIN
# ===============================
async def main():
    await start_webserver()
    await load_extensions(bot)
    await bot.start(BOT_TOKEN)

# ===============================
# ▶️ EJECUCIÓN
# ===============================
if __name__ == "__main__":
    if BOT_TOKEN:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            shutdown_type = "manual"
            print(Fore.MAGENTA + "🛑 Bot desconectado manualmente (KeyboardInterrupt).")
    else:
        print(Fore.RED + "❌ Error: BOT_TOKEN no está definido en el archivo .env")
