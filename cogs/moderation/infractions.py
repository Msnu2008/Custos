import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import logging
from db_operations import DBOperations

logger = logging.getLogger(__name__)

class Infractions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DBOperations(bot)

    @app_commands.command(name="infracciones", description="Muestra el historial disciplinario de un usuario.")
    @app_commands.default_permissions(administrator=True)
    async def infracciones(self, interaction: discord.Interaction, usuario: discord.Member):
        await interaction.response.defer(ephemeral=True)
        try:
            registros = await self.db.get_infractions(interaction.guild.id, usuario.id)

            if not registros:
                embed = discord.Embed(
                    title="📁 Historial limpio",
                    description=f"{usuario.mention} no tiene infracciones registradas.",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title=f"📄 Historial de {usuario}",
                    color=discord.Color.orange()
                )
                for r in registros:
                    fecha = datetime.fromisoformat(r['date']).strftime('%Y-%m-%d %H:%M')
                    moderador = interaction.guild.get_member(int(r['moderator_id']))
                    nombre_moderador = moderador.display_name if moderador else "Desconocido"
                    embed.add_field(
                        name=f"{r['type'].capitalize()} - {fecha}",
                        value=f"**Razón:** {r['reason']}\n**Moderador:** {nombre_moderador}",
                        inline=False
                    )
        except Exception as e:
            logger.error(f"Error al obtener historial: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="No se pudo obtener el historial de infracciones.",
                color=discord.Color.red()
            )
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Infractions(bot))
    logger.info("Cog Infractions cargado.")
