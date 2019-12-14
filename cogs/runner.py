import discord
import asyncio
import subprocess

from discord.ext import commands, tasks
from datetime import date, datetime


class Runner(commands.Cog):
    """This class runs the processes stored for the
    """
    def __init__(self, bot):
        self.bot = bot
        self.channel = None  # set in functions in case bot is not ready
        self.logging = True
        self.member_update.start()
        self.war_update.start()
        self.war_report.start()
        self.oak_google.start()
        self.rcs_wiki_update.start()
        self.rcs_location_check.start()

    def cog_unload(self):
        self.member_update.cancel()
        self.war_update.cancel()
        self.war_report.cancel()
        self.oak_google.cancel()
        self.rcs_wiki_update.cancel()
        self.rcs_location_check.cancel()

    async def run_process(self, command=None):
        """Executes the actual shell process"""
        command = f"python3 -W ignore::DeprecationWarning /home/tuba{command}"
        try:
            process = await asyncio.create_subprocess_shell(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = await process.communicate()
        except NotImplementedError:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = await self.bot.loop.run_in_executor(None, process.communicate)

        return [output.decode() for output in result]

    async def on_shell_error(self, command, response, errors):
        embed = discord.Embed(title=f"Errors for {command}", color=discord.Color.dark_red())
        embed.add_field(name="Output", value=response, inline=False)
        embed.add_field(name="Errors", value=f"```{errors[:1990]}```", inline=False)
        embed.set_footer(text=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        if not self.channel:
            self.channel = self.bot.get_channel(650896379178254346)
        return embed

    async def on_shell_success(self, command, response):
        embed = discord.Embed(title=f"Output for {command}", color=discord.Color.dark_green())
        embed.add_field(name="Output", value=response[:1995], inline=False)
        embed.set_footer(text=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        if not self.channel:
            self.channel = self.bot.get_channel(650896379178254346)
        return embed

    @tasks.loop(minutes=20)
    async def member_update(self):
        """Executes the rcsmembers.py command"""
        command = "/rcs/rcsmembers.py"
        response, errors = await self.run_process(command)
        if errors:
            embed = await self.on_shell_error(command, response, errors)
            return await self.channel.send(embed=embed)
        if self.logging:
            embed = await self.on_shell_success(command, response)
            return await self.channel.send(embed=embed)

    @member_update.before_loop
    async def before_member_update(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=10)
    async def war_update(self):
        command = "/rcs/warupdates.py"
        try:
            response, errors = await self.run_process(command)
        except:
            self.bot.logger.exception("war_udpate failed")
            return
        if errors:
            embed = await self.on_shell_error(command, response, errors)
            return await self.channel.send(embed=embed)
        if self.logging:
            embed = await self.on_shell_success(command, response)
            return await self.channel.send(embed=embed)

    @war_update.before_loop
    async def before_war_update(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=10)
    async def war_report(self):
        command = "/rcs/warreport.py"
        response, errors = await self.run_process(command)
        if errors:
            embed = await self.on_shell_error(command, response, errors)
            return await self.channel.send(embed=embed)
        if self.logging:
            embed = await self.on_shell_success(command, response)
            return await self.channel.send(embed=embed)

    @war_report.before_loop
    async def before_war_report(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=1)
    async def rcs_wiki_update(self):
        command = "/rcs/rcslist.py"
        response, errors = await self.run_process(command)
        if errors:
            embed = await self.on_shell_error(command, response, errors)
            return await self.channel.send(embed=embed)
        if self.logging:
            embed = await self.on_shell_success(command, response)
            return await self.channel.send(embed=embed)

    @rcs_wiki_update.before_loop
    async def before_rcs_wiki_update(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=24)
    async def rcs_location_check(self):
        # Only run on Wednesday
        if date.today().weekday() == 2:
            command = "/rcs/loccheck.py"
            response, errors = await self.run_process(command)
            if errors:
                embed = await self.on_shell_error(command, response, errors)
                return await self.channel.send(embed=embed)
            if self.logging:
                embed = await self.on_shell_success(command, response)
                return await self.channel.send(embed=embed)
        else:
            await self.channel.send("Skipping rcs_location_check. Today is not Wednesday.")

    @rcs_location_check.before_loop
    async def before_rcs_location_check(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=15)
    async def oak_google(self):
        command = "/coc/oak_google.py"
        response, errors = await self.run_process(command)
        if errors:
            embed = await self.on_shell_error(command, response, errors)
            return await self.channel.send(embed=embed)
        if self.logging:
            embed = await self.on_shell_success(command, response)
            return await self.channel.send(embed=embed)

    @oak_google.before_loop
    async def oak_google_update(self):
        await self.bot.wait_until_ready()

    @commands.command()
    async def flip(self, ctx):
        self.logging = not self.logging
        await ctx.send(f"Logging is now set to {self.logging}.")


def setup(bot):
    bot.add_cog(Runner(bot))
