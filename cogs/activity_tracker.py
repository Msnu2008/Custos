from discord.ext import commands
import datetime

class ActivityTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        db: commands.Cog = self.bot.get_cog("DBOperations")
        if not db:
            return

        is_ticket = await db.is_open_ticket_channel(str(message.channel.id))
        if is_ticket:
            await db.update_last_activity(str(message.channel.id), datetime.datetime.utcnow().isoformat())

async def setup(bot):
    await bot.add_cog(ActivityTracker(bot))
