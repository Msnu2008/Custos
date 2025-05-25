import discord
from discord.ext import tasks, commands
import datetime

INACTIVITY_THRESHOLD_MINUTES = 60  # ⚠️ Cambia esto si quieres más o menos tiempo

class InactivityChecker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_inactive_tickets.start()

    def cog_unload(self):
        self.check_inactive_tickets.cancel()

    @tasks.loop(minutes=5)
    async def check_inactive_tickets(self):
        now = datetime.datetime.utcnow()

        db: commands.Cog = self.bot.get_cog("DBOperations")
        if not db:
            print("DBOperations no está cargado")
            return

        tickets = await db.get_all_open_tickets()
        for ticket in tickets:
            try:
                channel_id = int(ticket['channel_id'])
                last_activity_str = ticket['last_activity']
                last_activity = datetime.datetime.fromisoformat(last_activity_str)

                elapsed_minutes = (now - last_activity).total_seconds() / 60
                if elapsed_minutes > INACTIVITY_THRESHOLD_MINUTES:
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        await channel.send("⏰ Este ticket ha estado inactivo por un buen tiempo. ¿Aún necesitas ayuda?")
            except Exception as e:
                print(f"Error procesando ticket inactivo: {e}")

    @check_inactive_tickets.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(InactivityChecker(bot))
