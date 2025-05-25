import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta, datetime
import logging
from db_operations import DBOperations  # Asegúrate de tener esta importación

logger = logging.getLogger(__name__)

class Actions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DBOperations(bot)

    async def send_dm(self, user: discord.User, title: str, reason: str):
        try:
            embed = discord.Embed(
                title=title,
                description=f"**Razón:** {reason}",
                color=discord.Color.red()
            )
            await user.send(embed=embed)
        except:
            logger.warning(f"No se pudo enviar DM a {user}.")

    async def log_mod_action(self, interaction: discord.Interaction, action_title: str, usuario: discord.Member, razon: str, color: discord.Color):
        try:
            modlog_channel_id = await self.db.get_modlog_channel(interaction.guild.id)
            modlog_channel = interaction.guild.get_channel(modlog_channel_id) if modlog_channel_id else None

            if modlog_channel:
                embed = discord.Embed(
                    title=action_title,
                    color=color,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Usuario", value=f"{usuario.mention} (`{usuario.id}`)", inline=False)
                embed.add_field(name="Moderador", value=f"{interaction.user.mention}", inline=False)
                embed.add_field(name="Razón", value=razon or "No especificada", inline=False)
                await modlog_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"[ModLog] Error al enviar al canal de modlog: {e}")

    @app_commands.command(name="ban", description="Banea permanentemente a un usuario del servidor.")
    @app_commands.default_permissions(administrator=True)
    async def ban(self, interaction: discord.Interaction, usuario: discord.Member, razon: str):
        await interaction.response.defer(ephemeral=True)
        await self.send_dm(usuario, "Has sido baneado", razon)
        await interaction.guild.ban(usuario, reason=razon)
        await interaction.followup.send(embed=discord.Embed(title="✅ Usuario baneado", description=f"{usuario.mention} ha sido baneado.\n**Razón:** {razon}", color=discord.Color.red()))
        await self.log_mod_action(interaction, "🔨 Usuario baneado", usuario, razon, discord.Color.red())

    @app_commands.command(name="expulsar", description="Expulsa a un usuario del servidor.")
    @app_commands.default_permissions(administrator=True)
    async def expulsar(self, interaction: discord.Interaction, usuario: discord.Member, razon: str):
        await interaction.response.defer(ephemeral=True)
        await self.send_dm(usuario, "Has sido expulsado", razon)
        await interaction.guild.kick(usuario, reason=razon)
        await interaction.followup.send(embed=discord.Embed(title="✅ Usuario expulsado", description=f"{usuario.mention} ha sido expulsado.\n**Razón:** {razon}", color=discord.Color.orange()))
        await self.log_mod_action(interaction, "👢 Usuario expulsado", usuario, razon, discord.Color.orange())

    @app_commands.command(name="mute", description="Silencia a un usuario por un tiempo determinado.")
    @app_commands.default_permissions(administrator=True)
    async def mute(self, interaction: discord.Interaction, usuario: discord.Member, tiempo: int, razon: str):
        await interaction.response.defer(ephemeral=True)
        duration = timedelta(minutes=tiempo)
        await usuario.timeout(duration, reason=razon)
        await interaction.followup.send(embed=discord.Embed(title="🔇 Usuario silenciado", description=f"{usuario.mention} ha sido silenciado por {tiempo} minutos.\n**Razón:** {razon}", color=discord.Color.dark_gray()))
        await self.log_mod_action(interaction, "🔇 Usuario silenciado", usuario, razon, discord.Color.dark_gray())

    @app_commands.command(name="unmute", description="Quita el silencio a un usuario.")
    @app_commands.default_permissions(administrator=True)
    async def unmute(self, interaction: discord.Interaction, usuario: discord.Member):
        await interaction.response.defer(ephemeral=True)
        await usuario.timeout(None)
        await interaction.followup.send(embed=discord.Embed(title="🔊 Silencio retirado", description=f"Se ha retirado el silencio a {usuario.mention}.", color=discord.Color.green()))
        await self.log_mod_action(interaction, "🔊 Silencio retirado", usuario, "Fin del mute", discord.Color.green())

async def setup(bot: commands.Bot):
    await bot.add_cog(Actions(bot))
    logger.info("Cog Actions cargado.")
