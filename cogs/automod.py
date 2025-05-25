import discord
from discord.ext import commands
from discord import app_commands

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_prohibited_words(self, guild_id):
        data = await self.bot.db.get_prohibited_words(guild_id)
        return data or []

    async def update_prohibited_words(self, guild_id, words):
        await self.bot.db.set_prohibited_words(guild_id, words)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        palabras = await self.get_prohibited_words(message.guild.id)
        contenido = message.content.lower()
        if any(p in contenido for p in palabras):
            try:
                await message.delete()
                await message.channel.send(
                    f"⚠️ {message.author.mention}, tu mensaje fue eliminado por contener una palabra prohibida.",
                    delete_after=5
                )
            except discord.Forbidden:
                print(f"No tengo permisos para eliminar mensajes en {message.guild.name}.")

    @app_commands.command(name="agregar_palabra", description="Agrega una palabra a la lista de moderación.")
    @app_commands.checks.has_permissions(administrator=True)
    async def agregar_palabra(self, interaction: discord.Interaction, palabra: str):
        palabra = palabra.lower()
        palabras = await self.get_prohibited_words(interaction.guild.id)
        if palabra in palabras:
            await interaction.response.send_message("❌ Esa palabra ya está en la lista.", ephemeral=True)
            return
        palabras.append(palabra)
        await self.update_prohibited_words(interaction.guild.id, palabras)
        await interaction.response.send_message(f"✅ Palabra **{palabra}** agregada a la lista.", ephemeral=True)

    @app_commands.command(name="eliminar_palabra", description="Elimina una palabra de la lista de moderación.")
    @app_commands.checks.has_permissions(administrator=True)
    async def eliminar_palabra(self, interaction: discord.Interaction, palabra: str):
        palabra = palabra.lower()
        palabras = await self.get_prohibited_words(interaction.guild.id)
        if palabra not in palabras:
            await interaction.response.send_message("❌ Esa palabra no está en la lista.", ephemeral=True)
            return
        palabras.remove(palabra)
        await self.update_prohibited_words(interaction.guild.id, palabras)
        await interaction.response.send_message(f"🗑️ Palabra **{palabra}** eliminada.", ephemeral=True)

    @app_commands.command(name="listar_palabras", description="Muestra la lista de palabras moderadas.")
    @app_commands.checks.has_permissions(administrator=True)
    async def listar_palabras(self, interaction: discord.Interaction):
        palabras = await self.get_prohibited_words(interaction.guild.id)
        if not palabras:
            await interaction.response.send_message("🚫 No hay palabras prohibidas configuradas.", ephemeral=True)
        else:
            texto = ', '.join(palabras)
            embed = discord.Embed(title="🚫 Palabras prohibidas", description=texto, color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
