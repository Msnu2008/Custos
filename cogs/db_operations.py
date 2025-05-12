from supabase import create_client, Client
import os
from discord.ext import commands
import datetime
from dotenv import load_dotenv
from discord import app_commands

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

class DBOperations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        bot.add_listener(self.on_ready, "on_ready")

    async def create_tables(self):
        try:
            self.supabase.from_('tickets').select('ticket_id').limit(1).execute()
            self.supabase.from_('ticket_reassignments').select('id').limit(1).execute()
        except Exception as e:
            print(f"Error al crear las tablas: {e}")

    def save_ticket(self, ticket_id, user_id, assigned_user_id, status, channel_id, created_at, reason=None, log=None):
        if log is None:
            log = []
        data = {
            'ticket_id': ticket_id,
            'user_id': user_id,
            'assigned_user_id': assigned_user_id,
            'status': status,
            'created_at': created_at.isoformat(),
            'channel_id': channel_id,
            'reason': reason,
            'log': log
        }
        try:
            response = self.supabase.table('tickets').insert(data).execute()
            return None if hasattr(response, 'error') and response.error else response.data
        except Exception as e:
            print(f"Error al guardar el ticket: {e}")
            return None

    def update_ticket_status(self, ticket_id, status, closed_at=None):
        data = {'status': status}
        if closed_at:
            data['closed_at'] = closed_at.isoformat()
        try:
            response = self.supabase.table('tickets').update(data).eq('ticket_id', ticket_id).execute()
            return None if hasattr(response, 'error') and response.error else response.data
        except Exception as e:
            print(f"Error al actualizar el ticket: {e}")
            return None

    def get_ticket_by_channel_id(self, channel_id):
        try:
            response = self.supabase.table('tickets').select('*').eq('channel_id', channel_id).execute()
            return None if hasattr(response, 'error') and response.error else (response.data[0] if response.data else None)
        except Exception as e:
            print(f"Error al obtener el ticket: {e}")
            return None

    def reassign_ticket(self, ticket_id, old_assigned_user_id, new_assigned_user_id):
        data = {
            'ticket_id': ticket_id,
            'old_assigned_user_id': old_assigned_user_id,
            'new_assigned_user_id': new_assigned_user_id,
            'reassigned_at': datetime.datetime.utcnow().isoformat()
        }
        try:
            response = self.supabase.table('ticket_reassignments').insert(data).execute()
            return None if hasattr(response, 'error') and response.error else response.data
        except Exception as e:
            print(f"Error al registrar la reasignación: {e}")
            return None

    def update_assigned_user(self, ticket_id, new_assigned_user_id):
        try:
            response = self.supabase.table('tickets').update({'assigned_user_id': new_assigned_user_id}).eq('ticket_id', ticket_id).execute()
            return None if hasattr(response, 'error') and response.error else response.data
        except Exception as e:
            print(f"Error al actualizar el asignado: {e}")
            return None

    def append_log(self, ticket_id, log_entry):
        try:
            response = self.supabase.table('tickets').select('log').eq('ticket_id', ticket_id).execute()
            if hasattr(response, 'error') and response.error:
                return None
            current_log = response.data[0]['log'] if response.data else []
            current_log.append(log_entry)
            update = self.supabase.table('tickets').update({'log': current_log}).eq('ticket_id', ticket_id).execute()
            return None if hasattr(update, 'error') and update.error else update.data
        except Exception as e:
            print(f"Error al añadir log: {e}")
            return None

    async def get_support_members(self, guild_id):
        try:
            response = self.supabase.table('config').select('support_role_id').eq('guild_id', guild_id).execute()
            if hasattr(response, 'error') and response.error:
                return None
            if not response.data:
                return None
            support_role_id = response.data[0]['support_role_id']
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                return None
            support_role = guild.get_role(int(support_role_id))
            if not support_role:
                return None
            return [m for m in guild.members if support_role in m.roles]
        except Exception as e:
            print(f"Error al obtener miembros de soporte: {e}")
            return None

    async def get_ticket_count(self, guild_id: int) -> int:
        try:
            response = self.supabase.table('tickets').select('ticket_id').execute()
            return 0 if hasattr(response, 'error') and response.error else len(response.data)
        except Exception as e:
            print(f"Error al contar tickets: {e}")
            return 0

    async def save_guild_config(self, guild_id: int, support_role_id: int = None, ticket_channel_id: int = None, ticket_category_id: int = None):
        try:
            response = self.supabase.table('config').select('guild_id').eq('guild_id', guild_id).execute()
            if hasattr(response, 'error') and response.error:
                return None

            data = {}
            if support_role_id is not None:
                data['support_role_id'] = support_role_id
            if ticket_channel_id is not None:
                 data['ticket_channel_id'] = ticket_channel_id

            if ticket_category_id is not None:
                data['ticket_category_id'] = ticket_category_id

            if response.data:
                update_response = self.supabase.table('config').update(data).eq('guild_id', guild_id).execute()
                return None if hasattr(update_response, 'error') and update_response.error else update_response.data
            else:
                insert_data = {'guild_id': guild_id, **data}
                insert_response = self.supabase.table('config').insert(insert_data).execute()
                return None if hasattr(insert_response, 'error') and insert_response.error else insert_response.data
        except Exception as e:
            print(f"Error al guardar config: {e}")
            return None

    async def get_guild_config(self, guild_id: int):
        try:
            response = self.supabase.table('config').select('support_role_id, ticket_channel_id, ticket_category_id').eq('guild_id', guild_id).execute()
            return None if hasattr(response, 'error') and response.error else (response.data[0] if response.data else None)
        except Exception as e:
            print(f"Error al obtener config: {e}")
            return None

    async def on_ready(self):
        await self.create_tables()

async def setup(bot):
    await bot.add_cog(DBOperations(bot))
