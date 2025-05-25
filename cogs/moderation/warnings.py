import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import logging
from db_operations import DBOperations

logger = logging.getLogger(__name__)

class Warnings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DBOperations(bot)

    @app_commands.command(name="advertir", description="Registra una advertencia para un usuario.")
    @app_commands.default_permissions(administrator=True)
    async def advertir(self, interaction: discord.Interaction, usuario: discord.Member, razon: str):
        await interaction.response.defer(ephemeral=True)
        try:
            await self.db.add_infraction(
                guild_id=interaction.guild.id,
                user_id=usuario.id,
                moderator_id=interaction.user.id,
                infraction_type="advertencia",
                reason=razon
            )
            embed = discord.Embed(
                title="⚠️ Advertencia registrada",
                description=f"{usuario.mention} ha recibido una advertencia.\n**Razón:** {razon}",
                color=discord.Color.orange()
            )
            await interaction.followup.send(embed=embed)

            # Enviar al canal de modlog si está configurado
            modlog_channel_id = await self.db.get_modlog_channel(interaction.guild.id)
            modlog_channel = interaction.guild.get_channel(modlog_channel_id) if modlog_channel_id else None

            if modlog_channel:
                modlog_embed = discord.Embed(
                    title="🚨 Nueva advertencia",
                    color=discord.Color.orange(),
                    timestamp=datetime.utcnow()
                )
                modlog_embed.add_field(name="Usuario", value=f"{usuario.mention} (`{usuario.id}`)", inline=False)
                modlog_embed.add_field(name="Moderador", value=f"{interaction.user.mention}", inline=False)
                modlog_embed.add_field(name="Razón", value=razon or "No especificada", inline=False)
                await modlog_channel.send(embed=modlog_embed)

        except Exception as e:
            logger.error(f"Error al registrar advertencia: {e}")
            error_embed = discord.Embed(
                title="❌ Error",
                description="No se pudo registrar la advertencia.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed)

    @app_commands.command(name="eliminar_advertencia", description="Elimina una advertencia de un usuario.")
    @app_commands.default_permissions(administrator=True)
    async def eliminar_advertencia(self, interaction: discord.Interaction, usuario: discord.Member):
        await interaction.response.defer(ephemeral=True)

        try:
            infracciones = await self.db.get_infractions(interaction.guild.id, usuario.id)
        except Exception as e:
            logger.error(f"Error al obtener infracciones para eliminar: {e}")
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ Error",
                    description="No se pudieron obtener las advertencias del usuario.",
                    color=discord.Color.red()
                )
            )

        advertencias = [i for i in infracciones if i['type'] == 'advertencia']

        if not advertencias:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="📂 Sin advertencias",
                    description=f"{usuario.mention} no tiene advertencias activas.",
                    color=discord.Color.green()
                )
            )

        options = []
        for i, adv in enumerate(advertencias):
            fecha = datetime.fromisoformat(adv['date']).strftime('%Y-%m-%d')
            label = f"{i+1}. {fecha} - {adv['reason'][:50]}"
            options.append(discord.SelectOption(label=label, value=str(adv['id'])))

        class AdvertenciaSelect(discord.ui.View):
            def __init__(self, db):
                super().__init__(timeout=60)
                self.db = db
                self.select = discord.ui.Select(
                    placeholder="Selecciona una advertencia para eliminar",
                    options=options
                )
                self.select.callback = self.on_select
                self.add_item(self.select)

            async def on_select(self, interaction_select: discord.Interaction):
                await interaction_select.response.defer(ephemeral=True)
                selected_id = self.select.values[0]
                try:
                    await self.db.delete_infraction(selected_id)
                    await interaction_select.followup.send(
                        content="✅ Advertencia eliminada correctamente.",
                        ephemeral=True
                    )
                except Exception as e:
                    logger.error(f"Error al eliminar advertencia: {e}")
                    await interaction_select.followup.send(
                        content="❌ No se pudo eliminar la advertencia.",
                        ephemeral=True
                    )

        await interaction.followup.send(
            embed=discord.Embed(
                title=f"🗑️ Eliminar advertencia de {usuario}",
                description="Selecciona una advertencia del menú para eliminarla. (Tienes 60 segundos)",
                color=discord.Color.red()
            ),
            view=AdvertenciaSelect(self.db)
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Warnings(bot))
    logger.info("Cog Warnings cargado.")
