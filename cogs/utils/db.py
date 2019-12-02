import asyncpg
import pymssql

from config import settings


class Sql:
    def __init__(self, as_dict=False):
        self.as_dict = as_dict

    def __enter__(self):
        self.conn = pymssql.connect(settings['database']['server'],
                                    settings['database']['username'],
                                    settings['database']['password'],
                                    settings['database']['database'],
                                    autocommit=True)
        self.cursor = self.conn.cursor(as_dict=self.as_dict)
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


class Psql:
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def create_pool():
        pool = await asyncpg.create_pool(f"{settings['pg']['uri']}/rcsdata", max_size=85)
        return pool

    async def get_clans(self):
        conn = self.bot.pool
        sql = "SELECT clan_name, clan_tag FROM rcs_clans ORDER BY clan_name"
        return await conn.fetch(sql)
