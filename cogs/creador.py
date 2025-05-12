import discord
from discord.ext import commands
import os
import sys

class CreadorCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
    
        # Determinamos el rango del ping para agregar el mensaje adecuado
        if latency < 100:
            status = "✅ ¡Excelente! El bot responde rápidamente."
        elif latency < 200:
            status = "⚠️ Bueno, pero podría haber un pequeño retraso."
        elif latency < 400:
            status = "❗ Aceptable, pero algo de latencia es notoria."
        else:
            status = "🚨 ¡Alto! El bot está experimentando mucha latencia."

        # Creamos el embed con el estado del ping
        embed = discord.Embed(
            title="Pong! 🏓", 
            description=f"Latencia: {latency}ms\n{status}",
            color=discord.Color.green()
        )
    
        await ctx.send(embed=embed)


    @commands.command(name="apagar")
    async def shutdown(self, ctx):
        if ctx.author.id == 737389521049616552:  # Reemplaza con tu ID de usuario
            embed = discord.Embed(title="Apagando el Bot", description="El bot se está apagando de forma segura...", color=discord.Color.orange())
            await ctx.send(embed=embed)
            await self.bot.close()
        else:
            embed = discord.Embed(title="Permisos Denegados", description="No tienes permisos para usar este comando.", color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(name="cargar")
    async def reload(self, ctx, cog: str):
        if ctx.author.id == 737389521049616552:  # Reemplaza con tu ID de usuario
            try:
                await self.bot.reload_extension(f"cogs.{cog}")
                embed = discord.Embed(title="Recarga de Extensión", description=f"La extensión `cogs.{cog}` ha sido recargada exitosamente.", color=discord.Color.green())
                await ctx.send(embed=embed)
            except commands.ExtensionNotLoaded:
                embed = discord.Embed(title="Error al Recargar", description=f"La extensión `cogs.{cog}` no está cargada.", color=discord.Color.red())
                await ctx.send(embed=embed)
            except commands.ExtensionNotFound:
                embed = discord.Embed(title="Error al Recargar", description=f"No se encontró la extensión `cogs.{cog}`.", color=discord.Color.red())
                await ctx.send(embed=embed)
            except Exception as e:
                embed = discord.Embed(title="Error al Recargar", description=f"Ocurrió un error al recargar `cogs.{cog}`:\n```{e}```", color=discord.Color.red())
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Permisos Denegados", description="No tienes permisos para usar este comando.", color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(name="eval")
    async def eval_code(self, ctx, *, code: str):
        if ctx.author.id == 737389521049616552:  # Reemplaza con tu ID de usuario
            try:
                result = eval(code)
                embed = discord.Embed(title="Resultado de la Evaluación", description=f"```{result}```", color=discord.Color.blurple())
                await ctx.send(embed=embed)
            except Exception as e:
                embed = discord.Embed(title="Error en la Evaluación", description=f"```{e}```", color=discord.Color.red())
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Permisos Denegados", description="No tienes permisos para usar este comando.", color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(name="sync")
    async def sync_commands(self, ctx):
        if ctx.author.id == 737389521049616552:  # Reemplaza con tu ID de usuario
            synced = await self.bot.tree.sync()
            embed = discord.Embed(title="Sincronización de Comandos", description=f"Se han sincronizado {len(synced)} comandos de aplicación globalmente.", color=discord.Color.green())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Permisos Denegados", description="No tienes permisos para usar este comando.", color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(name="info_bot")
    async def info_bot(self, ctx):
        if ctx.author.id == 737389521049616552:  # Reemplaza con tu ID de usuario
            uptime = (discord.utils.utcnow() - self.bot.user.created_at).total_seconds()
            servers = len(self.bot.guilds)
            embed = discord.Embed(title="Información del Bot", color=discord.Color.gold())
            embed.add_field(name="Uptime", value=f"{int(uptime)} segundos", inline=False)
            embed.add_field(name="Servidores", value=f"{servers} servidores", inline=False)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Permisos Denegados", description="No tienes permisos para usar este comando.", color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(name="dase_datos")
    async def db_check(self, ctx):
        if ctx.author.id == 737389521049616552:  # Reemplaza con tu ID de usuario
            embed = discord.Embed(title="Estado de la Base de Datos", description="Estado de la base de datos: OK.", color=discord.Color.green())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Permisos Denegados", description="No tienes permisos para usar este comando.", color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(name="mensaje_all")
    async def broadcast(self, ctx, *, message: str):
        if ctx.author.id == 737389521049616552:  # Reemplaza con tu ID de usuario
            for guild in self.bot.guilds:
                for channel in guild.text_channels:
                    try:
                        await channel.send(message)
                    except discord.Forbidden:
                        pass
                    except Exception as e:
                        print(f"Error al enviar broadcast en {guild.name} - {channel.name}: {e}")
            embed = discord.Embed(title="Broadcast Enviado", description="Mensaje enviado a todos los servidores.", color=discord.Color.green())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Permisos Denegados", description="No tienes permisos para usar este comando.", color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(name="serverlist")
    async def server_list(self, ctx):
        if ctx.author.id == 737389521049616552:  # Reemplaza con tu ID de usuario
            server_info = "\n".join([f"{guild.name} ({guild.id}) - {len(guild.members)} miembros" for guild in self.bot.guilds])
            embed = discord.Embed(title="Lista de Servidores", description=f"```\n{server_info}\n```", color=discord.Color.gold())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Permisos Denegados", description="No tienes permisos para usar este comando.", color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(name="exec")
    async def exec_command(self, ctx, *, command: str):
        if ctx.author.id == 737389521049616552:  # Reemplaza con tu ID de usuario
            os.system(command)
            embed = discord.Embed(title="Comando Ejecutado", description=f"Comando `{command}` ejecutado.", color=discord.Color.green())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Permisos Denegados", description="No tienes permisos para usar este comando.", color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(name="setstatus")
    async def set_status(self, ctx, status_type: str, *, message: str):
        if ctx.author.id == 737389521049616552:  # Reemplaza con tu ID de usuario
            status = discord.Status.online if status_type == "online" else discord.Status.idle
            await self.bot.change_presence(status=status, activity=discord.Game(name=message))
            embed = discord.Embed(title="Estado del Bot Cambiado", description=f"Estado cambiado a {status_type}: {message}", color=discord.Color.blue())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Permisos Denegados", description="No tienes permisos para usar este comando.", color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(name="debug")
    async def debug(self, ctx):
        if ctx.author.id == 737389521049616552:  # Reemplaza con tu ID de usuario
            embed = discord.Embed(title="Información de Depuración", description="Información de depuración: OK.", color=discord.Color.green())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Permisos Denegados", description="No tienes permisos para usar este comando.", color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(name="forcerestart")
    async def force_restart(self, ctx):
        if ctx.author.id == 737389521049616552:  # Reemplaza con tu ID de usuario
            embed = discord.Embed(title="Reiniciando el Bot", description="Forzando el reinicio del bot...", color=discord.Color.orange())
            await ctx.send(embed=embed)
            os.execv(sys.executable, ['python'] + sys.argv)
        else:
            embed = discord.Embed(title="Permisos Denegados", description="No tienes permisos para usar este comando.", color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(name="reiniciar")
    async def reiniciar_comando(self, ctx):
        if ctx.author.id == 737389521049616552:  # Reemplaza con tu ID de usuario
            embed = discord.Embed(title="Reiniciando el Bot", description="Reiniciando el bot de forma segura...", color=discord.Color.orange())
            await ctx.send(embed=embed)
            await self.bot.close()
        else:
            embed = discord.Embed(title="Permisos Denegados", description="No tienes permisos para usar este comando.", color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(name="ayuda")
    async def ayuda(self, ctx):
        embed = discord.Embed(
            title="Comandos del Creador",
            description="Lista de comandos exclusivos para el creador del bot.",
            color=discord.Color.blue()
        )
        embed.add_field(name="$ping", value="Mide la latencia del bot.", inline=False)
        embed.add_field(name="$apagar", value="Apaga el bot de forma segura.", inline=False)
        embed.add_field(name="$cargar <cog>", value="Recarga una extensión del bot.", inline=False)
        embed.add_field(name="$eval <código>", value="Ejecuta código Python.", inline=False)
        embed.add_field(name="$sync", value="Sincroniza los comandos de la aplicación.", inline=False)
        embed.add_field(name="$info_bot", value="Muestra información del bot.", inline=False)
        embed.add_field(name="$base_datos", value="Verifica el estado de la base de datos.", inline=False)
        embed.add_field(name="$mensaje_all <mensaje>", value="Envía un mensaje a todos los servidores.", inline=False)
        embed.add_field(name="$serverlist", value="Muestra la lista de servidores.", inline=False)
        embed.add_field(name="$exec <comando>", value="Ejecuta un comando en el sistema.", inline=False)
        embed.add_field(name="$setstatus <tipo> <mensaje>", value="Cambia el estado del bot.", inline=False)
        embed.add_field(name="$debug", value="Muestra información técnica útil.", inline=False)
        embed.add_field(name="$forcerestart", value="Reinicia el bot (forzado).", inline=False)
        embed.add_field(name="$reiniciar", value="Reinicia el bot de forma segura.", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CreadorCommands(bot))