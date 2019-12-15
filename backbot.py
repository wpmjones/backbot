import git
import asyncio
import sys
import os
import traceback
import coc

from discord.ext import commands
from cogs.utils.db import Psql
from loguru import logger
from config import settings

enviro = "LIVE"
token = settings['discord']['tubatime_token']
prefix = "2ba."

if enviro == "LIVE":
    coc_name = "war"
elif enviro == "home":
    coc_name = "war_home"
else:
    coc_name = "war_dev"

initial_extensions = ["cogs.admin",
                      "cogs.runner",
                      "cogs.warreport",
                      ]

coc_client = coc.login(settings['supercell']['user'],
                       settings['supercell']['pass'],
                       key_names=coc_name,
                       correct_tags=True)


class BackBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=prefix,
                         description="Private Background Task Bot",
                         case_insensitive=True)
        self.coc = coc_client
        self.logger = logger

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
                self.logger.info(f"{extension} loaded successfully")
            except Exception as extension:
                self.logger.error(f"Failed to load extension {extension}.", file=sys.stderr)
                traceback.print_exc()

    async def on_ready(self):
        logger.info("Tuba Time has started")

    async def close(self):
        await super().close()
        await self.coc.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        pool = loop.run_until_complete(Psql.create_pool())
        bot = BackBot()
        bot.repo = git.Repo(os.getcwd())
        bot.pool = pool
        bot.loop = loop
        bot.run(token, reconnect=True)
    except:
        traceback.print_exc()
