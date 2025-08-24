"""Guild converter."""
from settings import CONFIG

def get_guild_rank(guild_rp: int):
    """Get guild rank from rp held."""
    rp_map = [
        24, 48, 96, 144, 192, 240, 288, 360, 432,
        504, 600, 696, 792, 888, 984, 1080, 1200,
    ]
    for i, u in enumerate(rp_map):
        if guild_rp < u:
            return i
    return 17

def get_guild_max_members(guild_rank: int):
    """Get max guild memebers from config by guild rank."""
    for u in reversed(CONFIG.erupe.clan_member_limits):
        if guild_rank >= u[0]:
            return u[1]
    return 0

def max_members(guild_rp: int):
    """Get max guild members from guild rp."""
    return get_guild_max_members(get_guild_rank(guild_rp))
