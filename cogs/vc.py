import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import logging

logger = logging.getLogger(__name__)

class VoiceManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_vcs = {}  # guild_id: {user_id: channel_id}

    @app_commands.command(name="vc_setup", description="Configura la categoría para canales de voz dinámicos.")
    @app_commands.checks.has_permissions(administrator=True)
    async def vc_setup(self, interaction: discord.Interaction, category: discord.CategoryChannel):
        """Define la categoría donde se crearán los canales temporales."""
        try:
            await self.bot.db.set_vc_config(interaction.guild.id, category.id, None)
            await interaction.response.send_message(
                f"Categoría de canales de voz configurada: {category.name}", ephemeral=True)
        except Exception as e:
            logger.error(f"Error en vc_setup: {e}")
            await interaction.response.send_message("Error al configurar la categoría de VC.", ephemeral=True)

    @app_commands.command(name="set_vc", description="Configura el canal señuelo para la creación de canales de voz.")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_vc(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        """Define el canal señuelo que al unirse genera un canal temporal."""
        try:
            config = await self.bot.db.get_vc_config(interaction.guild.id)
            if not config or not config.get('category_id'):
                await interaction.response.send_message(
                    "Primero debes configurar la categoría con /vc_setup.", ephemeral=True)
                return
            await self.bot.db.set_vc_config(interaction.guild.id, config['category_id'], channel.id)
            await interaction.response.send_message(
                f"Canal señuelo configurado: {channel.name}", ephemeral=True)
        except Exception as e:
            logger.error(f"Error en set_vc: {e}")
            await interaction.response.send_message("Error al configurar el canal señuelo.", ephemeral=True)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        guild = member.guild
        config = await self.bot.db.get_vc_config(guild.id)
        if not config or not config.get("category_id") or not config.get("senuelo_id"):
            return

        category = guild.get_channel(int(config["category_id"]))
        senuelo_id = int(config["senuelo_id"])

        # Si usuario entra al canal señuelo, crea canal temporal
        if after.channel and after.channel.id == senuelo_id:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(connect=False),
                member: discord.PermissionOverwrite(connect=True, manage_channels=True, mute_members=True, deafen_members=True, move_members=True),
            }
            new_channel = await guild.create_voice_channel(
                name=f"{member.display_name}'s channel",
                category=category,
                overwrites=overwrites,
                user_limit=0,
                reason="Canal temporal creado por sistema VC"
            )
            await member.move_to(new_channel)

            if guild.id not in self.active_vcs:
                self.active_vcs[guild.id] = {}
            self.active_vcs[guild.id][member.id] = new_channel.id

        # Si usuario sale de canal temporal y queda vacío, espera 1 minuto para eliminar canal
        if before.channel and before.channel.category_id == category.id:
            channel_id = before.channel.id
            if channel_id in self.active_vcs.get(guild.id, {}).values():
                if len(before.channel.members) == 0:
                    await asyncio.sleep(60)  # Espera 60 segundos antes de borrar
                    channel = guild.get_channel(channel_id)
                    if channel and len(channel.members) == 0:
                        try:
                            await channel.delete(reason="Canal temporal vacío eliminado automáticamente después de 1 minuto")
                            # Elimina de la memoria
                            user_to_remove = None
                            for uid, cid in self.active_vcs[guild.id].items():
                                if cid == channel_id:
                                    user_to_remove = uid
                                    break
                            if user_to_remove:
                                del self.active_vcs[guild.id][user_to_remove]
                        except Exception as e:
                            logger.error(f"Error eliminando canal temporal: {e}")

    @app_commands.command(name="vc_lock", description="Bloquea el canal de voz actual")
    async def vc_lock(self, interaction: discord.Interaction):
        voice_channel = interaction.user.voice.channel if interaction.user.voice else None
        if not voice_channel:
            await interaction.response.send_message("No estás conectado a ningún canal de voz.", ephemeral=True)
            return
        
        vc_config = await self.bot.db.get_vc_config(interaction.guild.id)
        if voice_channel.id == vc_config.get('senuelo_id'):
            await interaction.response.send_message("No puedes bloquear el canal señuelo.", ephemeral=True)
            return

        overwrite = voice_channel.overwrites_for(interaction.guild.default_role)
        overwrite.connect = False
        await voice_channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)

        await interaction.response.send_message(f"🔒 Canal **{voice_channel.name}** bloqueado para todos los usuarios.", ephemeral=True)

    @app_commands.command(name="vc_unlock", description="Desbloquea el canal de voz bloqueado")
    async def vc_unlock(self, interaction: discord.Interaction):
        voice_channel = interaction.user.voice.channel if interaction.user.voice else None
        if not voice_channel:
            await interaction.response.send_message("No estás conectado a ningún canal de voz.", ephemeral=True)
            return

        overwrite = voice_channel.overwrites_for(interaction.guild.default_role)
        overwrite.connect = None
        await voice_channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)

        await interaction.response.send_message(f"🔓 Canal **{voice_channel.name}** desbloqueado.", ephemeral=True)

    @app_commands.command(name="vc_limit", description="Establece límite de usuarios para el canal de voz")
    @app_commands.describe(limit="Cantidad máxima de usuarios (0 para sin límite)")
    async def vc_limit(self, interaction: discord.Interaction, limit: int):
        voice_channel = interaction.user.voice.channel if interaction.user.voice else None
        if not voice_channel:
            await interaction.response.send_message("No estás conectado a ningún canal de voz.", ephemeral=True)
            return
        if limit < 0:
            await interaction.response.send_message("El límite debe ser 0 o mayor.", ephemeral=True)
            return

        await voice_channel.edit(user_limit=limit)
        if limit == 0:
            await interaction.response.send_message(f"🔄 Límite removido en **{voice_channel.name}**.", ephemeral=True)
        else:
            await interaction.response.send_message(f"🔢 Límite establecido a {limit} en **{voice_channel.name}**.", ephemeral=True)

    @app_commands.command(name="vc_rename", description="Renombra el canal de voz")
    @app_commands.describe(new_name="Nuevo nombre para el canal")
    async def vc_rename(self, interaction: discord.Interaction, new_name: str):
        voice_channel = interaction.user.voice.channel if interaction.user.voice else None
        if not voice_channel:
            await interaction.response.send_message("No estás conectado a ningún canal de voz.", ephemeral=True)
            return
        
        if len(new_name) > 100:
            await interaction.response.send_message("El nombre es muy largo (máximo 100 caracteres).", ephemeral=True)
            return

        await voice_channel.edit(name=new_name)
        await interaction.response.send_message(f"✏️ El canal fue renombrado a **{new_name}**.", ephemeral=True)

    @app_commands.command(name="vc_claim", description="Reclama el canal si el dueño se desconectó")
    async def vc_claim(self, interaction: discord.Interaction):
        voice_channel = interaction.user.voice.channel if interaction.user.voice else None
        if not voice_channel:
            await interaction.response.send_message("No estás conectado a ningún canal de voz.", ephemeral=True)
            return

        vc_data = await self.bot.db.get_vc_channel_owner(voice_channel.id)  # Debes implementar este método en tu DB
        if not vc_data:
            await interaction.response.send_message("Este canal no tiene dueño registrado.", ephemeral=True)
            return

        owner_id = int(vc_data['owner_id'])
        owner_member = interaction.guild.get_member(owner_id)
        if owner_member and owner_member.voice and owner_member.voice.channel == voice_channel:
            await interaction.response.send_message("El dueño del canal todavía está conectado.", ephemeral=True)
            return

        await self.bot.db.set_vc_channel_owner(voice_channel.id, interaction.user.id)  # Implementa este método también
        await interaction.response.send_message(f"✅ Has reclamado el canal **{voice_channel.name}**.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(VoiceManager(bot))
