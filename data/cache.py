"""
Universal Cache Class object
"""
from typing import List

class GuildRecruitment():
    """Recruitment Guild Cache Object"""
    def __init__(
        self,
        gid: int,
        name: str,
        leader: str,
        members: int
    ):
        self.gid: int = gid
        self.name: str = name
        self.leader: str = leader
        self.members: int = members

class GuildCharacterDetails():
    """Guild Character Details Cache Object"""
    def __init__(
        self,
        guild_id: int,
        discord_id: str,
        character_id: int,
        character_name: str,
        order_index: int,
        selected: int
    ):
        self.guild_id: int = guild_id
        self.discord_id: str = discord_id
        self.character_id: int = character_id
        self.character_name: str = character_name
        self.order_index: int = order_index
        self.selected: int = selected

class Cache():
    """Cache object."""
    def __init__(self) -> None:
        self._list_guilds: List[GuildRecruitment] = None
        self._list_guild_character_details: list[GuildCharacterDetails] = None

    @property
    def guilds(self):
        """The list_guilds property."""
        return self._list_guilds

    @guilds.setter
    def guilds(self, value):
        self._list_guilds = value

    @guilds.deleter
    def guilds(self):
        del self._list_guilds

    @property
    def guild_character_details(self):
        """The list_guild_character_details property."""
        return self._list_guild_character_details

    @guild_character_details.setter
    def guild_character_details(self, value):
        self._list_guild_character_details = value

    @guild_character_details.deleter
    def guild_character_details(self):
        del self._list_guild_character_details

cache = Cache()
