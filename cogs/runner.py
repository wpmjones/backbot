import asyncio
import subprocess

from discord.ext import commands, tasks


class Runner(commands.Cog):
    """This class runs the processes stored for the
    """
    def __init__(self, bot):
        self.bot = bot
        self.channel = None  # set in functions in case bot is not ready
        self.member_update.start()
        self.war_update.start()

    def cog_unload(self):
        self.member_update.cancel()
        self.war_update.cancel()

    async def run_process(self, command=None):
        """Executes the actual shell process"""
        command = f"python3 /home/pj/rcs/{command}"
        try:
            process = await asyncio.create_subprocess_shell(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = await process.communicate()
        except NotImplementedError:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = await self.bot.loop.run_in_executor(None, process.communicate)

        stdout, stderr = [output.decode() for output in result]

        if stderr:
            text = f'Output:\n{stdout}\nErrors:\n{stderr}'
        else:
            text = stdout

        return text

    @tasks.loop(minutes=15)
    async def member_update(self):
        """Executes the rcsmembers.py command"""
        command = "rcsmembers.py"
        response = await self.run_process(command)
        if not self.channel:
            self.channel = self.bot.get_channel(650896379178254346)
        await self.channel.send(f"```{response}```")

    @member_update.before_loop
    async def before_member_update(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=15)
    async def war_update(self):
        """Executes the rcsmembers.py command"""
        command = "test.py"
        response = await self.run_process(command)
        if not self.channel:
            self.channel = self.bot.get_channel(650896379178254346)
        await self.channel.send(f"```{response}```")

    @war_update.before_loop
    async def before_war_update(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Runner(bot))
