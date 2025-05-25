import discord
from discord.ext import commands
from discord import app_commands
import logging
from db_operations import DBOperations

logger = logging.getLogger(__name__)

class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DBOperations(bot)

    @app_commands.command(name="report", description="Reporta a un usuario al staff del servidor.")
    async def report(self, interaction: discord.Interaction, usuario: discord.Member, razon: str):
        await interaction.response.defer(ephemeral=True)

        if usuario == interaction.user:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ No puedes reportarte a ti mismo",
                    color=discord.Color.red()
                )
            )

        try:
            # Obtener canal de reportes desde la configuración
            config = await self.db.get_guild_config(interaction.guild.id)
            report_channel_id = config.get("report_channel_id") if config else None

            if not report_channel_id:
                return await interaction.followup.send(
                    embed=discord.Embed(
                        title="⚙️ Canal no configurado",
                        description="No se ha configurado un canal para recibir reportes. Usa `/set_report`.",
                        color=discord.Color.orange()
                    )
                )

            canal = interaction.guild.get_channel(int(report_channel_id))
            if not canal:
                return await interaction.followup.send(
                    embed=discord.Embed(
                        title="❌ Error",
                        description="No se pudo encontrar el canal configurado para reportes.",
                        color=discord.Color.red()
                    )
                )

            embed = discord.Embed(
                title="📢 Nuevo Reporte",
                description=f"**Usuario reportado:** {usuario.mention}\n"
                            f"**Reportado por:** {interaction.user.mention}\n"
                            f"**Razón:** {razon}",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Servidor: {interaction.guild.name}")
            await canal.send(embed=embed)

            await interaction.followup.send(
                embed=discord.Embed(
                    title="✅ Reporte enviado",
                    description=f"Tu reporte contra {usuario.mention} ha sido enviado al staff.",
                    color=discord.Color.green()
                )
            )

        except Exception as e:
            logger.error(f"Error al enviar reporte: {e}")
            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ Error",
                    description="Ocurrió un error al enviar el reporte.",
                    color=discord.Color.red()
                )
            )

    @app_commands.command(name="set_report", description="Configura el canal donde se enviarán los reportes.")
    @app_commands.default_permissions(administrator=True)
    async def set_report(self, interaction: discord.Interaction, canal: discord.TextChannel):
        await interaction.response.defer(ephemeral=True)

        try:
            config = await self.db.get_guild_config(str(interaction.guild.id)) or {}
            success = await self.db.save_guild_config(
                str(interaction.guild.id),
                support_role_id=config.get("support_role_id", "0"),
                ticket_channel_id=config.get("ticket_channel_id", "0"),
                ticket_category_id=config.get("ticket_category_id", "0"),
                announcement_channel_id=config.get("announcement_channel_id", "0"),
                report_channel_id=str(canal.id)  # Aquí se guarda correctamente
            )

            if success:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="✅ Canal configurado",
                        description=f"Los reportes se enviarán a {canal.mention}.",
                        color=discord.Color.green()
                    ),
                    ephemeral=True
                )
            else:
                raise Exception("Fallo al guardar en Supabase.")

        except Exception as e:
            logger.error(f"Error al guardar canal de reportes: {e}")
            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ Error",
                    description="No se pudo guardar el canal de reportes.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
async def setup(bot: commands.Bot):
    await bot.add_cog(Report(bot))
    logger.info("Cog Report cargado.")