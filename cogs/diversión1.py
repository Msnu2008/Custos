import discord
from discord.ext import commands
import random
import aiohttp
import asyncio
from discord import app_commands

class Diversion1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="8ball")
    async def eight_ball(self, interaction: discord.Interaction, *, pregunta: str):
        await interaction.response.defer(ephemeral=True)
        respuestas = [
            "Sí.", "No.", "Tal vez.", "Definitivamente sí.", "Definitivamente no.",
            "Pregunta más tarde.", "No puedo decirlo ahora.", "Probablemente.", "Difícil de decir."
        ]
        respuesta = random.choice(respuestas)
        await interaction.followup.send(f"🎱 Pregunta: **{pregunta}**\n🔮 Respuesta: **{respuesta}**", ephemeral=True)

    @app_commands.command(name="moneda")
    async def coinflip(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        resultado = random.choice(["🪙 Cara", "🪙 Cruz"])
        await interaction.followup.send(f"Resultado del lanzamiento: **{resultado}**", ephemeral=True)

    @app_commands.command(name="dado")
    async def dado(self, interaction: discord.Interaction, caras: int = 6):
        await interaction.response.defer(ephemeral=True)
        if caras < 1:
            await interaction.followup.send("El número de caras debe ser mayor que 0.", ephemeral=True)
        else:
            numero = random.randint(1, caras)
            await interaction.followup.send(f"🎲 Has lanzado un dado de {caras} caras y salió: **{numero}**", ephemeral=True)

    @app_commands.command(name="rps")
    async def rps(self, interaction: discord.Interaction, eleccion: str):
        await interaction.response.defer(ephemeral=True)
        opciones = ["piedra", "papel", "tijera"]
        eleccion = eleccion.lower()
        if eleccion not in opciones:
            await interaction.followup.send("Por favor elige: piedra, papel o tijera.", ephemeral=True)
            return
        bot_eleccion = random.choice(opciones)
        if eleccion == bot_eleccion:
            resultado = "¡Empate!"
        elif (eleccion == "piedra" and bot_eleccion == "tijera") or \
             (eleccion == "papel" and bot_eleccion == "piedra") or \
             (eleccion == "tijera" and bot_eleccion == "papel"):
            resultado = "¡Ganaste!"
        else:
            resultado = "¡Perdiste!"
        await interaction.followup.send(f"Elegiste **{eleccion}**, yo elegí **{bot_eleccion}**. {resultado}", ephemeral=True)

    @app_commands.command(name="meme")
    async def meme(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        subreddit = "memesesp"  # Prueba con este primero
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://meme-api.com/r/{subreddit}") as r:
                if r.status == 200:
                    data = await r.json()
                    embed = discord.Embed(title=data["title"], color=discord.Color.random())
                    embed.set_image(url=data["url"])
                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    await interaction.followup.send(f"No se pudo obtener un meme de {subreddit} 😞", ephemeral=True)
                    
    @app_commands.command(name="chiste")
    async def chiste(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        chistes = [
            "¿Por qué los pájaros no usan Facebook? Porque ya tienen Twitter.",
            "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!",
            "—¡Camarero! Este filete tiene muchos nervios. —Normal, es la primera vez que se lo comen."
        ]
        await interaction.followup.send(random.choice(chistes), ephemeral=True)

    @app_commands.command(name="insulto")
    async def insulto(self, interaction: discord.Interaction, usuario: discord.Member):
        await interaction.response.defer(ephemeral=True)
        insultos = [
            f"{usuario.mention}, eres tan lento que cuando corres parece que estás pausado.",
            f"{usuario.mention}, tu WiFi va más rápido que tus ideas.",
            f"{usuario.mention}, no eres tonto, solo tienes mala suerte pensando."
        ]
        await interaction.followup.send(random.choice(insultos), ephemeral=True)

    @app_commands.command(name="halago")
    async def halago(self, interaction: discord.Interaction, usuario: discord.Member):
        await interaction.response.defer(ephemeral=True)
        halagos = [
            f"{usuario.mention}, eres más brillante que una supernova 💫.",
            f"{usuario.mention}, tienes una sonrisa que ilumina servidores ☀️.",
            f"{usuario.mention}, si fueras un emoji serías ⭐."
        ]
        await interaction.followup.send(random.choice(halagos), ephemeral=True)

    @app_commands.command(name="ship")
    async def ship(self, interaction: discord.Interaction, user1: discord.Member, user2: discord.Member):
        await interaction.response.defer(ephemeral=True)
        porcentaje = random.randint(0, 100)
        nombre = user1.name[:len(user1.name)//2] + user2.name[len(user2.name)//2:]
        await interaction.followup.send(f"💖 {user1.mention} + {user2.mention} = **{nombre}**\nCompatibilidad: **{porcentaje}%**", ephemeral=True)

    @app_commands.command(name="compatibilidad")
    async def compatibilidad(self, interaction: discord.Interaction, usuario: discord.Member):
        await interaction.response.defer(ephemeral=True)
        porcentaje = random.randint(0, 100)
        await interaction.followup.send(f"❤️ Tu compatibilidad con {usuario.mention} es de **{porcentaje}%**", ephemeral=True)

    @app_commands.command(name="simparometro")
    async def simparometro(self, interaction: discord.Interaction, usuario: discord.Member):
        await interaction.response.defer(ephemeral=True)
        porcentaje = random.randint(0, 100)
        await interaction.followup.send(f"😳 {usuario.mention} es **{porcentaje}% simp**", ephemeral=True)

    @app_commands.command(name="gayrate")
    async def gayrate(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        porcentaje = random.randint(0, 100)
        await interaction.followup.send(f"🌈 Hoy eres **{porcentaje}% gay**, según mis sensores.", ephemeral=True)

    @app_commands.command(name="inteligenciametro")
    async def inteligenciametro(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        iq = random.randint(50, 160)
        await interaction.followup.send(f"🧠 Tu IQ estimado es de **{iq}** puntos.", ephemeral=True)

    @app_commands.command(name="abrazo")
    async def abrazo(self, interaction: discord.Interaction, miembro: discord.Member):
        await interaction.response.defer(ephemeral=True)
        gifs = [
            "https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif",
            "https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif",
            "https://media.giphy.com/media/wnsgren9NtITS/giphy.gif"
        ]
        embed = discord.Embed(description=f"🤗 {interaction.user.mention} le da un abrazo a {miembro.mention}!", color=discord.Color.pink())
        embed.set_image(url=random.choice(gifs))
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="beso")
    async def beso(self, interaction: discord.Interaction, miembro: discord.Member):
        await interaction.response.defer(ephemeral=True)
        gifs = [
            "https://media.giphy.com/media/11k3oaUjSlFR4I/giphy.gif",
            "https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif",
            "https://media.giphy.com/media/FqBTvSNjNzeZG/giphy.gif"
        ]
        embed = discord.Embed(description=f"😘 {interaction.user.mention} le da un beso a {miembro.mention}!", color=discord.Color.red())
        embed.set_image(url=random.choice(gifs))
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="golpe")
    async def golpe(self, interaction: discord.Interaction, miembro: discord.Member):
        await interaction.response.defer(ephemeral=True)
        gifs = [
            "https://media.giphy.com/media/xUOwGchzwhfny7ztqE/giphy.gif",
            "https://media.giphy.com/media/Zau0yrl17uzdK/giphy.gif",
            "https://media.giphy.com/media/ARSp9T7wwxNcs/giphy.gif"
        ]
        embed = discord.Embed(description=f"🥊 {interaction.user.mention} golpea a {miembro.mention}!", color=discord.Color.dark_red())
        embed.set_image(url=random.choice(gifs))
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="adivina")
    async def adivina(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        numero = random.randint(1, 10)
        await interaction.followup.send("Estoy pensando en un número del 1 al 10. ¡Adivina cuál es!", ephemeral=True)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            mensaje = await self.bot.wait_for("message", check=check, timeout=10)
            if mensaje.content.isdigit() and int(mensaje.content) == numero:
                await interaction.followup.send("🎉 ¡Correcto!", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ No era ese. El número era **{numero}**", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send(f"⏰ Se acabó el tiempo. El número era **{numero}**", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Diversion1(bot))