import discord
from discord.ext import commands
import random
import aiohttp
import asyncio
from discord import app_commands
class Diversion2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot    

    @app_commands.command(name="patada")
    async def patada(self, ctx, miembro: discord.Member):
            gifs = [
                "https://media.giphy.com/media/l1J9EdzfOSgfyueLm/giphy.gif",
                "https://media.giphy.com/media/12MEJ5zsZRPsNW/giphy.gif",
                "https://media.giphy.com/media/RXGNsyRb1hDJm/giphy.gif"
            ]
            embed = discord.Embed(description=f"🦶 {ctx.author.mention} le da una patada a {miembro.mention}!", color=discord.Color.orange())
            embed.set_image(url=random.choice(gifs))
            await ctx.send(embed=embed)

    @app_commands.command(name="bailar")
    async def bailar(self, ctx):
        gifs = [
            "https://media.giphy.com/media/l0MYOUI5XfRkTPv8s/giphy.gif",
            "https://media.giphy.com/media/3o7abldj0b3rxrZUxW/giphy.gif",
            "https://media.giphy.com/media/l0MYDGA6k3bLw6IP2/giphy.gif"
        ]
        embed = discord.Embed(description=f"💃 {ctx.author.mention} se pone a bailar!", color=discord.Color.blue())
        embed.set_image(url=random.choice(gifs))
        await ctx.send(embed=embed)

    @app_commands.command(name="preguntatrivia")
    async def preguntatrivia(self, ctx):
        trivias = [
            ("¿Cuál es el planeta más grande del sistema solar?", "jupiter"),
            ("¿Cuántos corazones tiene un pulpo?", "3"),
            ("¿Qué año empezó la Segunda Guerra Mundial?", "1939")
        ]
        pregunta, respuesta_correcta = random.choice(trivias)
        await ctx.send(f"🧠 Pregunta: **{pregunta}**")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            mensaje = await self.bot.wait_for("message", check=check, timeout=15)
            if mensaje.content.lower() == respuesta_correcta:
                await ctx.send("🎉 ¡Respuesta correcta!")
            else:
                await ctx.send(f"❌ Incorrecto. La respuesta era **{respuesta_correcta}**.")
        except asyncio.TimeoutError:
            await ctx.send("⏰ ¡Se acabó el tiempo!")

    @app_commands.command(name="mathgame")
    async def mathgame(self, ctx):
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        resultado = a + b
        await ctx.send(f"🧮 ¿Cuánto es **{a} + {b}**?")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            mensaje = await self.bot.wait_for("message", check=check, timeout=8)
            if mensaje.content.isdigit() and int(mensaje.content) == resultado:
                await ctx.send("✅ ¡Correcto!")
            else:
                await ctx.send(f"❌ Incorrecto. La respuesta era **{resultado}**.")
        except asyncio.TimeoutError:
            await ctx.send("⏰ ¡Tiempo agotado!")

    @app_commands.command(name="animalfusion")
    async def animalfusion(self, ctx, animal1: str, animal2: str):
            nombre_fusionado = animal1[:len(animal1)//2] + animal2[len(animal2)//2:]
            await ctx.send(f"🧬 Has creado un nuevo animal: **{nombre_fusionado.capitalize()}**")

    @app_commands.command(name="dictador")
    async def dictador(self, ctx):
        miembros = ctx.guild.members
        elegido = random.choice([m for m in miembros if not m.bot])
        await ctx.send(f"🪖 Hoy el dictador del servidor es: {elegido.mention} ¡Obedézcanle!")

async def setup(bot):
    await bot.add_cog(Diversion2(bot))

    