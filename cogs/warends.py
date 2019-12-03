import coc

from discord.ext import commands, tasks


class WarEnds(commands.Cog):
    """This class exists solely to pull the latest information from the API and
    update the database
    """

    def __init__(self, bot):
        self.bot = bot
        self.war_ends.start()

    def cog_unload(self):
        self.war_ends.cancel()

    @tasks.loop(minutes=10)
    async def war_ends(self):
        """Check war log for missing wars, then check current war"""
        conn = self.bot.pool
        sql = "SELECT clan_tag FROM rcs_clans WHERE war_log_public = 1"
        fetch = await conn.fetch(sql)
        for row in fetch:
            tag = row[0]
            self.bot.logger.info(f"Checking for war end for: {tag}")
            try:
                war = await self.bot.coc.get_clan_war(tag)
            except coc.PrivateWarLog:
                sql = "UPDATE rcs_clans SET war_log_public = 0 WHERE clan_tag = $1"
                await conn.execute(sql, tag)
                continue
            if war.state == "warEnded":
                try:
                    sql = ("UPDATE rcs_wars SET "
                           "clan_stars = $1, clan_destruction = $2, clan_attacks = $3, "
                           "opponent_stars $4, opponent_destruction = $5, opponent_attacks = $6, "
                           "war_state = 'warEnded', end_time = $7)"
                           "VALUES ($1, $2, $3, $4, $5, $6, $7)")
                    await conn.execute(sql, war.clan.stars, war.clan.destruction, war.clan.attacks_used,
                                       war.opponent.stars, war.opponent.destruction, war.opponent.attacks_used,
                                       war.end_time.time)
                except:
                    self.bot.logger.exception("fail")

    @war_ends.before_loop
    async def before_war_ends(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(WarEnds(bot))

