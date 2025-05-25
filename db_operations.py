import os
import asyncio
from discord.ext import commands
from supabase import create_client, Client

class DBOperations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )

    async def get_all_open_tickets(self):
        def fetch():
            try:
                return self.supabase.table('tickets').select('*').eq('status', 'open').execute()
            except Exception:
                return None

        response = await asyncio.to_thread(fetch)
        return response.data if response and response.data else []

    async def create_ticket(self, guild_id: int, channel_id: int, user_id: int, status: str = 'open'):
        def insert():
            try:
                return self.supabase.table('tickets').insert({
                    'guild_id': guild_id,
                    'channel_id': channel_id,
                    'user_id': user_id,
                    'status': status,
                    'last_activity': None
                }).execute()
            except Exception:
                return None

        response = await asyncio.to_thread(insert)
        return response.data if response else None

    async def update_ticket_status(self, channel_id: int, status: str):
        def update():
            try:
                return self.supabase.table('tickets').update({'status': status}).eq('channel_id', channel_id).execute()
            except Exception:
                return None

        response = await asyncio.to_thread(update)
        return response is not None

    async def update_ticket_last_activity(self, channel_id: int, timestamp):
        def update():
            try:
                return self.supabase.table('tickets').update({'last_activity': timestamp}).eq('channel_id', channel_id).execute()
            except Exception:
                return None

        response = await asyncio.to_thread(update)
        return response is not None

    async def get_server_config(self, guild_id: int):
        def fetch():
            try:
                return self.supabase.table('server_config').select('*').eq('guild_id', guild_id).single().execute()
            except Exception:
                return None

        response = await asyncio.to_thread(fetch)
        return response.data if response else None

    async def update_server_config(self, guild_id: int, config_data: dict):
        def update():
            try:
                return self.supabase.table('server_config').update(config_data).eq('guild_id', guild_id).execute()
            except Exception:
                return None

        response = await asyncio.to_thread(update)
        return response is not None

    async def save_guild_config(self, guild_id: str, support_role_id: str = "0", ticket_channel_id: str = "0", ticket_category_id: str = "0", announcement_channel_id: str = "0", modlog_channel_id: str = None, report_channel_id: str = None):
        try:
            data = {
                "guild_id": guild_id,
                "support_role_id": support_role_id,
                "ticket_channel_id": ticket_channel_id,
                "ticket_category_id": ticket_category_id,
                "announcement_channel_id": announcement_channel_id,
                "modlog_channel_id": modlog_channel_id,
                "report_channel_id": report_channel_id
            }
            data = {k: v for k, v in data.items() if v is not None}
            existing = await self.get_server_config(guild_id)
            if existing:
                response = self.supabase.table("server_config").update(data).eq("guild_id", guild_id).execute()
            else:
                response = self.supabase.table("server_config").insert(data).execute()
            return response is not None
        except Exception:
            return False

async def setup(bot):
    await bot.add_cog(DBOperations(bot))
