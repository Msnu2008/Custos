import discord
from discord.ext import commands
from discord import app_commands
import logging
import asyncio

logger = logging.getLogger(__name__)

class TicketButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎟️ Crear Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket_button")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        try:
            db_cog = interaction.client.get_cog("DBOperations")
            if not db_cog:
                await interaction.followup.send("❌ Error: Sistema de tickets no configurado.", ephemeral=True)
                return

            guild_config = await db_cog.get_server_config(str(interaction.guild_id))
            if not guild_config:
                await interaction.followup.send("❌ El servidor no ha configurado el sistema de tickets.", ephemeral=True)
                return

            support_role_id = guild_config.get("support_role_id")
            ticket_category_id = guild_config.get("ticket_category_id")
            if not support_role_id or not ticket_category_id:
                await interaction.followup.send("❌ Configuración incompleta de tickets.", ephemeral=True)
                return

            support_role = interaction.guild.get_role(int(support_role_id))
            ticket_category = interaction.guild.get_channel(int(ticket_category_id))
            if not support_role or not ticket_category:
                await interaction.followup.send("❌ No se encontró rol de soporte o categoría.", ephemeral=True)
                return

            ticket_name = f"ticket-{interaction.user.name.lower()}-{interaction.user.discriminator}"
            for channel in interaction.guild.text_channels:
                if channel.name == ticket_name:
                    await interaction.followup.send("❌ Ya tienes un ticket abierto.", ephemeral=True)
                    return

            ticket_channel = await ticket_category.create_text_channel(
                ticket_name,
                topic=f"Ticket de {interaction.user.display_name}"
            )
            await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True, read_message_history=True)
            await ticket_channel.set_permissions(support_role, read_messages=True, send_messages=True, read_message_history=True)
            await ticket_channel.set_permissions(interaction.guild.default_role, read_messages=False)

            embed = discord.Embed(
                title="🎫 Ticket creado",
                description=f"{interaction.user.mention}, un miembro del soporte te atenderá pronto.",
                color=discord.Color.green()
            )
            close_view = discord.ui.View()

            close_button = discord.ui.Button(
                label="🔒 Cerrar Ticket",
                style=discord.ButtonStyle.red,
                custom_id=f"close_ticket_{ticket_channel.id}"
            )

            async def close_callback(close_interaction: discord.Interaction):
                if not any(role.id == int(support_role_id) for role in close_interaction.user.roles):
                    await close_interaction.response.send_message("❌ Solo el staff puede cerrar tickets.", ephemeral=True)
                    return
                await close_interaction.response.send_message("🔒 Cerrando el ticket...", ephemeral=True)
                await asyncio.sleep(1)
                if ticket_channel and ticket_channel.permissions_for(ticket_channel.guild.me).manage_channels:
                    await ticket_channel.delete()

            close_button.callback = close_callback
            close_view.add_item(close_button)

            await ticket_channel.send(content=f"{interaction.user.mention} {support_role.mention}", embed=embed, view=close_view)
            await interaction.followup.send(f"✅ Ticket creado: {ticket_channel.mention}", ephemeral=True)

        except Exception as e:
            logger.error(f"Error creando ticket: {e}")
            await interaction.followup.send(f"❌ Error al crear ticket: {e}", ephemeral=True)


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="create_ticket_panel", description="Crea un panel con botón para crear tickets.")
    @app_commands.default_permissions(administrator=True)
    async def create_ticket_panel(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog("DBOperations")
        if not db_cog:
            await interaction.followup.send("❌ Error: DBOperations no cargado.", ephemeral=True)
            return

        config = await db_cog.get_server_config(str(interaction.guild_id))
        if not config or not config.get("support_role_id") or not config.get("ticket_category_id"):
            await interaction.followup.send("❌ Debes configurar primero el rol de soporte y categoría con /set_support_role y /set_ticket_category.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🎫 Sistema de Tickets",
            description="Haz clic en el botón para crear un ticket.",
            color=discord.Color.green()
        )
        view = TicketButtonView()
        await interaction.channel.send(embed=embed, view=view)
        await interaction.followup.send("✅ Panel de tickets creado.", ephemeral=True)

    @app_commands.command(name="anunciar", description="Envía un anuncio al canal de anuncios.")
    @app_commands.describe(mensaje="Mensaje del anuncio")
    @app_commands.default_permissions(administrator=True)
    async def anunciar(self, interaction: discord.Interaction, mensaje: str):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog("DBOperations")
        if not db_cog:
            await interaction.followup.send("❌ Error: DBOperations no cargado.", ephemeral=True)
            return

        try:
            config = await db_cog.get_server_config(str(interaction.guild.id))
            canal_id = config.get("announcement_channel_id") if config else None

            if not canal_id:
                await interaction.followup.send("❌ No hay canal de anuncios configurado.", ephemeral=True)
                return

            canal = interaction.guild.get_channel(int(canal_id))
            if canal is None:
                await interaction.followup.send("❌ Canal de anuncios no encontrado.", ephemeral=True)
                return

            await canal.send(
                content=f"{mensaje}\n\n_Anuncio enviado por {interaction.user.mention}_",
                allowed_mentions=discord.AllowedMentions.all()
            )

            await interaction.followup.send(
                embed=discord.Embed(
                    title="✅ Anuncio enviado",
                    description=f"Tu mensaje fue enviado correctamente a {canal.mention}.",
                    color=discord.Color.green()
                ),
                ephemeral=True
            )

        except Exception as e:
            logger.error(f"Error al enviar anuncio: {e}")
            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ Error",
                    description="Ocurrió un error al intentar enviar el anuncio.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    @app_commands.command(name="set_support_role", description="Configura el rol de soporte para tickets.")
    @app_commands.describe(role="Rol que podrá ver y gestionar los tickets.")
    @app_commands.default_permissions(administrator=True)
    async def set_support_role(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog("DBOperations")
        if not db_cog:
            await interaction.followup.send("❌ Error: DBOperations no cargado.", ephemeral=True)
            return

        config = await db_cog.get_server_config(str(interaction.guild_id)) or {}
        ticket_channel_id = config.get("ticket_channel_id", "0")
        ticket_category_id = config.get("ticket_category_id", "0")

        success = await db_cog.save_guild_config(str(interaction.guild_id), str(role.id), ticket_channel_id, ticket_category_id)
        if success:
            await interaction.followup.send(f"✅ Rol de soporte configurado: **{role.name}**.", ephemeral=True)
        else:
            await interaction.followup.send("❌ Error al guardar configuración.", ephemeral=True)

    @app_commands.command(name="set_ticket_category", description="Configura la categoría donde se crearán los tickets.")
    @app_commands.describe(category="Categoría donde se crearán los tickets.")
    @app_commands.default_permissions(administrator=True)
    async def set_ticket_category(self, interaction: discord.Interaction, category: discord.CategoryChannel):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog("DBOperations")
        if not db_cog:
            await interaction.followup.send("❌ Error: DBOperations no cargado.", ephemeral=True)
            return

        config = await db_cog.get_server_config(str(interaction.guild_id)) or {}
        support_role_id = config.get("support_role_id", "0")
        ticket_channel_id = config.get("ticket_channel_id", "0")

        success = await db_cog.save_guild_config(str(interaction.guild_id), support_role_id, ticket_channel_id, str(category.id))
        if success:
            await interaction.followup.send(f"✅ Categoría para tickets configurada: **{category.name}**.", ephemeral=True)
        else:
            await interaction.followup.send("❌ Error al guardar configuración.", ephemeral=True)

    @app_commands.command(name="set_anuncios", description="Establece este canal como canal de anuncios.")
    @app_commands.default_permissions(administrator=True)
    async def set_anuncios(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog("DBOperations")
        if not db_cog:
            await interaction.followup.send("❌ Error: DBOperations no cargado.", ephemeral=True)
            return

        config = await db_cog.get_server_config(str(interaction.guild.id)) or {}
        support_role_id = config.get("support_role_id", "0")
        ticket_channel_id = config.get("ticket_channel_id", "0")
        ticket_category_id = config.get("ticket_category_id", "0")

        success = await db_cog.save_guild_config(
            str(interaction.guild.id),
            support_role_id,
            ticket_channel_id,
            ticket_category_id,
            announcement_channel_id=str(interaction.channel.id)
        )
        if success:
            await interaction.followup.send("✅ Canal de anuncios configurado correctamente.", ephemeral=True)
        else:
            await interaction.followup.send("❌ Error al guardar el canal de anuncios.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
