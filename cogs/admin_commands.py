import discord
from discord.ext import commands, tasks
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

class TicketButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        logger.info("TicketButtonView inicializada (persistente).")

    @discord.ui.button(label="🎟️ Crear Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket_button")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        try:
            db_cog = interaction.client.get_cog("DBOperations")
            if not db_cog:
                await interaction.followup.send('❌ Error: Sistema de tickets no configurado.', ephemeral=True)
                return

            guild_config = await db_cog.get_guild_config(str(interaction.guild_id))
            if not guild_config:
                await interaction.followup.send('❌ El servidor no ha configurado el sistema de tickets.', ephemeral=True)
                return

            support_role_id = guild_config.get('support_role_id')
            ticket_category_id = guild_config.get('ticket_category_id')

            if not support_role_id or not ticket_category_id:
                await interaction.followup.send('❌ Configuración de tickets incompleta. Contacta a un administrador.', ephemeral=True)
                return

            # Convertir ticket_category_id a entero
            ticket_category_id_int = int(ticket_category_id)

            # Verificar si ya existe un ticket abierto del usuario
            existing_tickets = [
                channel for channel in interaction.guild.text_channels
                if channel.category_id == ticket_category_id_int and
                channel.name.startswith(f"ticket-{interaction.user.name.lower()}-{interaction.user.discriminator}")
            ]

            if existing_tickets:
                await interaction.followup.send('❌ Ya tienes un ticket abierto. Ciérralo antes de crear uno nuevo.', ephemeral=True)
                return

            support_role = interaction.guild.get_role(int(support_role_id))
            ticket_category = interaction.guild.get_channel(ticket_category_id_int)

            if not support_role or not ticket_category:
                await interaction.followup.send('❌ No se encontró el rol de soporte o la categoría de tickets.', ephemeral=True)
                return

            # Crear canal de ticket
            ticket_name = f"ticket-{interaction.user.name.lower()}-{interaction.user.discriminator}"
            ticket_channel = await ticket_category.create_text_channel(
                ticket_name,
                topic=f"Ticket de {interaction.user.display_name}"
            )

            await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True, read_message_history=True)
            await ticket_channel.set_permissions(support_role, read_messages=True, send_messages=True, read_message_history=True)

            # Embed y botón de cerrar ticket
            ticket_embed = discord.Embed(
                title="🎫 Ticket Creado",
                description=f"Bienvenido {interaction.user.mention}. Un miembro del equipo de soporte te atenderá pronto.",
                color=discord.Color.green()
            )

            close_view = discord.ui.View()
            close_button = discord.ui.Button(
                label="🔒 Cerrar Ticket",
                style=discord.ButtonStyle.red,
                custom_id=f"close_ticket_{ticket_channel.id}"
            )

            async def close_ticket_callback(close_interaction: discord.Interaction):
                if not any(role.id == int(support_role_id) for role in close_interaction.user.roles):
                    await close_interaction.response.send_message('❌ Solo el personal de soporte puede cerrar tickets.', ephemeral=True)
                    return

                await close_interaction.response.defer()
                await ticket_channel.delete()

            close_button.callback = close_ticket_callback
            close_view.add_item(close_button)

            await ticket_channel.send(
                content=f"{interaction.user.mention} {support_role.mention}",
                embed=ticket_embed,
                view=close_view
            )

            await interaction.followup.send(f'✅ Tu ticket ha sido creado en {ticket_channel.mention}', ephemeral=True)
            logger.info(f"Ticket creado por {interaction.user.name} en {interaction.guild.name}")

        except Exception as e:
            await interaction.followup.send(f'❌ Error al crear el ticket: {str(e)}', ephemeral=True)
            logger.error(f"Error al crear ticket: {str(e)}")


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.keep_alive.start()
        logger.info("Cog AdminCommands inicializado.")

    @app_commands.command(name="create_ticket_panel", description="Crea un panel de tickets con un botón para abrir tickets.")
    @app_commands.default_permissions(administrator=True)
    async def create_ticket_panel(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        db_cog = self.bot.get_cog("DBOperations")
        if db_cog:
            guild_config = await db_cog.get_guild_config(str(interaction.guild_id))
            if not guild_config or not guild_config.get('support_role_id') or not guild_config.get('ticket_category_id'):
                await interaction.followup.send('❌ Primero configura el rol de soporte y la categoría de tickets usando `/set_support_role` y `/set_ticket_category`.', ephemeral=True)
                return

            embed = discord.Embed(
                title="🎫 Sistema de Tickets",
                description="Haz clic en el botón de abajo para crear un ticket y recibir ayuda.",
                color=discord.Color.green()
            )
            ticket_view = TicketButtonView()

            try:
                await interaction.channel.send(embed=embed, view=ticket_view)
                await interaction.followup.send('✅ Panel de tickets creado exitosamente.', ephemeral=True)
                logger.info(f"Panel de tickets creado en el servidor {interaction.guild.name} ({interaction.guild_id})")
            except Exception as e:
                await interaction.followup.send(f'❌ Error al crear el panel de tickets: {str(e)}', ephemeral=True)
                logger.error(f"Error al crear el panel de tickets en {interaction.guild.id}: {str(e)}")
        else:
            await interaction.followup.send('❌ Error: El cog DBOperations no está cargado.', ephemeral=True)
            logger.error("DBOperations cog no encontrado.")

    @app_commands.command(name="set_support_role", description="Establece el rol de soporte para el sistema de tickets.")
    @app_commands.default_permissions(administrator=True)
    async def set_support_role(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog("DBOperations")
        if db_cog:
            if role is None:
                await interaction.followup.send("❌ Debes especificar un rol de soporte.", ephemeral=True)
                return

            existing_config = await db_cog.get_guild_config(str(interaction.guild_id))
            category_id = existing_config.get('ticket_category_id', '0') if existing_config else '0'

            success = await db_cog.save_guild_config(
                str(interaction.guild_id),
                str(role.id),
                "0",  # ticket_channel_id no usado aún
                category_id
            )

            if success:
                await interaction.followup.send(f'✅ Rol de soporte establecido: **{role.name}**.', ephemeral=True)
                logger.info(f"Rol de soporte {role.name} guardado en DB para {interaction.guild.name}")
            else:
                await interaction.followup.send('❌ Error al guardar el rol en la base de datos.', ephemeral=True)
        else:
            await interaction.followup.send('❌ Error: El cog DBOperations no está cargado.', ephemeral=True)

    @app_commands.command(name="set_ticket_category", description="Establece la categoría donde se crearán los tickets.")
    @app_commands.default_permissions(administrator=True)
    async def set_ticket_category(self, interaction: discord.Interaction, category: discord.CategoryChannel):
        await interaction.response.defer(ephemeral=True)
        db_cog = self.bot.get_cog("DBOperations")
        if db_cog:
            if category is None:
                await interaction.followup.send("❌ Debes especificar una categoría de tickets.", ephemeral=True)
                return

            existing_config = await db_cog.get_guild_config(str(interaction.guild_id))
            support_role_id = existing_config.get('support_role_id', '0') if existing_config else '0'

            success = await db_cog.save_guild_config(
                str(interaction.guild_id),
                support_role_id,
                "0",
                str(category.id)
            )

            if success:
                await interaction.followup.send(f'✅ Categoría de tickets establecida: **{category.name}**.', ephemeral=True)
                logger.info(f"Categoría de tickets {category.name} guardada en DB para {interaction.guild.name}")
            else:
                await interaction.followup.send('❌ Error al guardar la categoría en la base de datos.', ephemeral=True)
        else:
            await interaction.followup.send('❌ Error: El cog DBOperations no está cargado.', ephemeral=True)

    @tasks.loop(seconds=60)
    async def keep_alive(self):
        await self.bot.change_presence(activity=discord.Game(name="Manteniéndome activo"))
        logger.info("Ping para mantener el bot activo.")

    def cog_unload(self):
        self.keep_alive.cancel()


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))
    logger.info("Cog AdminCommands cargado.")
