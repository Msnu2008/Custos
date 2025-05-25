import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

class Messages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="limpiar", description="Elimina mensajes recientes en un canal.")
    @app_commands.default_permissions(administrator=True)
    async def limpiar(self, interaction: discord.Interaction, cantidad: int):
        await interaction.response.defer(ephemeral=True)

        if cantidad < 1 or cantidad > 100:
            await interaction.followup.send("❌ Debes ingresar una cantidad entre 1 y 100.")
            return

        deleted = await interaction.channel.purge(limit=cantidad)
        embed = discord.Embed(
            title="🧹 Limpieza realizada",
            description=f"Se eliminaron {len(deleted)} mensajes.",
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="slowmode", description="Activa el modo lento en un canal.")
    @app_commands.default_permissions(administrator=True)
    async def slowmode(self, interaction: discord.Interaction, segundos: int):
        await interaction.response.defer(ephemeral=True)

        if segundos < 0 or segundos > 21600:
            await interaction.followup.send("❌ El valor debe estar entre 0 y 21600 segundos.")
            return

        await interaction.channel.edit(slowmode_delay=segundos)
        embed = discord.Embed(
            title="🐌 Modo lento activado",
            description=f"Los usuarios solo podrán enviar mensajes cada {segundos} segundos.",
            color=discord.Color.purple()
        )
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Messages(bot))
    logger.info("Cog Messages cargado.")
