import discord
from discord.ext import commands
from discord.ui import Button, View
from datetime import datetime
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

SUPABASE_URL = SUPABASE_URL.replace('\\x3a', ':')  # Reemplaza '\\x3a' por ':'


class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        bot.add_listener(self.on_ready, "on_ready")

    async def on_ready(self):
        print(f"Bot {self.bot.user} conectado y listo.")

    async def create_ticket(self, user_id, guild_id, channel_id):
        # Asegúrate de obtener la configuración de la base de datos para cada servidor
        guild_config = await self.get_guild_config(guild_id)
        if not guild_config:
            print(f"No se encontró configuración para el servidor {guild_id}.")
            return None

        # Verificar si el usuario ya tiene un ticket abierto
        existing_ticket = await self.get_ticket_by_user(user_id)
        if existing_ticket:
            return existing_ticket

        # Crear un nuevo ticket en la base de datos
        ticket_id = await self.save_ticket(user_id, guild_id, channel_id)
        if not ticket_id:
            return None

        # Crear un canal para el ticket
        category_id = guild_config.get('ticket_category_id')
        category = discord.utils.get(self.bot.get_guild(guild_id).categories, id=category_id)
        if category:
            channel = await self.bot.get_guild(guild_id).create_text_channel(f'ticket-{ticket_id}', category=category)
        else:
            channel = await self.bot.get_guild(guild_id).create_text_channel(f'ticket-{ticket_id}')

        # Agregar el usuario al canal
        await channel.set_permissions(user_id, read_messages=True, send_messages=True)

        return {
            "ticket_id": ticket_id,
            "channel": channel
        }

    async def save_ticket(self, user_id, guild_id, channel_id):
        # Guarda el ticket en Supabase
        ticket_data = {
            'user_id': user_id,
            'guild_id': guild_id,
            'status': 'open',
            'created_at': datetime.utcnow().isoformat(),
            'channel_id': channel_id,
            'reason': None,
            'log': []
        }
        response = self.supabase.table('tickets').insert(ticket_data).execute()
        if response.error:
            print(f"Error al guardar el ticket: {response.error}")
            return None
        return response.data[0]['ticket_id']

    async def get_ticket_by_user(self, user_id):
        # Obtiene el ticket del usuario desde la base de datos
        response = self.supabase.table('tickets').select('*').eq('user_id', user_id).eq('status', 'open').execute()
        if response.error or not response.data:
            return None
        return response.data[0]

    async def get_ticket_by_channel_id(self, channel_id):
        # Obtiene el ticket asociado al canal
        response = self.supabase.table('tickets').select('*').eq('channel_id', channel_id).execute()
        if response.error or not response.data:
            return None
        return response.data[0]

    async def close_ticket(self, channel_id):
        # Cierra un ticket
        ticket = await self.get_ticket_by_channel_id(channel_id)
        if not ticket:
            return None

        ticket_id = ticket['ticket_id']
        closed_at = datetime.utcnow().isoformat()
        self.supabase.table('tickets').update({'status': 'closed', 'closed_at': closed_at}).eq('ticket_id', ticket_id).execute()

        return ticket_id

    async def get_guild_config(self, guild_id: int):
        # Obtiene la configuración del servidor desde la base de datos
        response = self.supabase.table('config').select('support_role_id, ticket_channel_id, ticket_category_id').eq('guild_id', guild_id).execute()
        if response.error or not response.data:
            return None
        return response.data[0]

    @discord.ui.button(label="Crear Ticket", style=discord.ButtonStyle.green)
    async def create_ticket_button(self, interaction: discord.Interaction, button_obj: Button):
        # Crea un ticket cuando se presiona el botón
        user_id = interaction.user.id
        guild_id = interaction.guild.id
        channel_id = interaction.channel.id

        ticket = await self.create_ticket(user_id, guild_id, channel_id)
        if ticket:
            await interaction.response.send_message(f"¡Ticket creado! Canal: {ticket['channel'].mention}", ephemeral=True)
        else:
            await interaction.response.send_message("Hubo un error al crear el ticket.", ephemeral=True)

    @discord.ui.button(label="Cerrar Ticket", style=discord.ButtonStyle.danger)
    async def close_ticket_button(self, interaction: discord.Interaction, button_obj: Button):
        # Cierra el ticket cuando se presiona el botón
        channel_id = interaction.channel.id
        ticket_id = await self.close_ticket(channel_id)
        if ticket_id:
            await interaction.response.send_message(f"Ticket cerrado. ID del ticket: {ticket_id}", ephemeral=True)
        else:
            await interaction.response.send_message("No se encontró un ticket asociado a este canal.", ephemeral=True)

    @discord.ui.button(label="Llamar a Staff", style=discord.ButtonStyle.secondary)
    async def call_staff_button(self, interaction: discord.Interaction, button_obj: Button):
        # Llamar a un miembro del staff (puedes agregar funcionalidades adicionales aquí)
        staff_members = await self.get_support_members(interaction.guild.id)
        if staff_members:
            staff_list = [staff.mention for staff in staff_members]
            await interaction.response.send_message(f"Miembros de soporte: {', '.join(staff_list)}", ephemeral=True)
        else:
            await interaction.response.send_message("No se encontraron miembros de soporte.", ephemeral=True)

    async def get_support_members(self, guild_id):
        # Obtén los miembros con rol de soporte
        guild_config = await self.get_guild_config(guild_id)
        if not guild_config:
            return None
        support_role_id = guild_config['support_role_id']
        guild = self.bot.get_guild(guild_id)
        support_role = discord.utils.get(guild.roles, id=support_role_id)
        if not support_role:
            return None
        return [member for member in guild.members if support_role in member.roles]


async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
