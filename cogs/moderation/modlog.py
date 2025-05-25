import discord
from discord.ext import commands
from discord import app_commands
import logging
from db_operations import DBOperations

class MiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DBOperations(bot)  # <- ¡esto es lo importante!

logger = logging.getLogger(__name__)

class ModLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DBOperations(bot)


    @app_commands.command(name="modlog", description="Habilita o deshabilita el canal de logs de moderación.")
    @app_commands.default_permissions(administrator=True)
    async def modlog(self, interaction: discord.Interaction, canal: discord.TextChannel):
        await interaction.response.defer(ephemeral=True)

        try:
            await self.db.set_modlog_channel(interaction.guild.id, canal.id)
            embed = discord.Embed(
                title="📋 Canal de logs configurado",
                description=f"Los eventos de moderación serán enviados a {canal.mention}.",
                color=discord.Color.blue()
            )
        except Exception as e:
            logger.error(f"Error al guardar canal de logs: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Ocurrió un error al guardar el canal de logs.",
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(ModLog(bot))
    logger.info("Cog ModLog cargado.")
