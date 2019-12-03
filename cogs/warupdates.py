import coc

from discord.ext import commands, tasks


class WarUpdates(commands.Cog):
    """This class exists solely to pull the latest information from the API and
    update the database
    """
    def __init__(self, bot):
        self.bot = bot
        self.war_updates.start()

    def cog_unload(self):
        self.war_updates.cancel()

    @tasks.loop(minutes=10)
    async def war_updates(self):
        """Check war log for missing wars, then check current war"""
        conn = self.bot.pool
        sql = "SELECT clan_tag FROM rcs_clans WHERE war_log_public = 1"
        fetch = await conn.fetch(sql)
        for row in fetch:
            tag = row[0]
            # check war log for missing wars
            try:
                war_log = await self.bot.coc.get_warlog(tag, cache=False)
            except coc.PrivateWarLog:
                sql = "UPDATE rcs_clans SET war_log_public = 0 WHERE clan_tag = $1"
                await conn.execute(sql, tag)
                continue
            self.bot.logger.info(f"Checking war log for: {tag}")
            try:
                print("start try")
                for war in war_log:
                    print(war.clan.destruction)
                    if war.clan.destruction > 100:
                        # Ignore CWL wars
                        continue
                    opponent_name = war.opponent_name.replace("'", "''")
                    sql = ("INSERT INTO rcs_wars (clan_tag, clan_stars, clan_destruction, clan_attacks, "
                           "opponent_tag, opponent_name, opponent_stars, opponent_destruction, opponent_attacks, "
                           "team_size, war_state, end_time, reported, war_type)"
                           "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14) "
                           "ON CONFLICT (clan_tag, end_time) DO NOTHING")
                    await conn.execute(sql, war.clan.tag[1:], war.clan.stars, war.clan.destruction, war.clan.attacks_used,
                                       war.opponent.tag[1:], opponent_name, war.opponent.stars, war.opponent.destruction,
                                       war.opponent.attacks_used, war.team_size, war.state, war.end_time.time,
                                       1, "random")
                print("end try")
            except:
                self.bot.logger.exception("fail")
            # check for current war
            self.bot.logger.info(f"Checking current war for: {tag}")
            war = await self.bot.coc.get_clan_war(tag)
            if war.state in ['preparation', 'inWar']:
                opponent_name = war.opponent.name.replace("'", "''")
                try:
                    sql = ("INSERT INTO rcs_wars (clan_tag, clan_stars, clan_destruction, clan_attacks, "
                           "opponent_tag, opponent_name, opponent_stars, opponent_destruction, opponent_attacks, "
                           "team_size, war_state, start_time, end_time, reported, war_type)"
                           "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15) "
                           "ON CONFLICT (clan_tag, end_time) DO NOTHING")
                    await conn.execute(sql, war.clan.tag[1:], war.clan.stars, war.clan.destruction, war.clan.attacks_used,
                                       war.opponent.tag[1:], opponent_name, war.opponent.stars, war.opponent.destruction,
                                       war.opponent.attacks_used, war.team_size, war.state,
                                       war.preparation_start_time.time, war.end_time.time, 0, war.type)
                except:
                    self.bot.logger.exception("fail")

    @war_updates.before_loop
    async def before_war_updates(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(WarUpdates(bot))

