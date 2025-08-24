"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy.dialects.postgresql import (
    VARCHAR
)

from ...base_mapping import Base

class GuildCharactersByGuildId(Base):
    """Guild Characters by Guild Id view object"""

    __query__ = """
    CREATE OR REPLACE VIEW guild_characters_by_id AS
    SELECT
        guild_characters.id,
        guild_characters.guild_id,
        guilds.name AS guild_name,
        users.id AS uid,
        users.psn_id,
        discord.discord_id as discord_id,
        characters.id AS character_id,
        characters.name AS character_name,
        characters.weapon_type,
        characters.gr,
        characters.hr,
        characters.gcp,
        characters.kouryou_point,
        characters.netcafe_points,
        characters.promo_points,
        characters.daily_quests,
        characters.bonus_quests,
        characters.last_login,
        date_part('epoch'::text, characters.daily_time) AS daily_time,
        guild_characters.order_index,
        guild_characters.avoid_leadership,
        guild_characters.rp_today,
        guild_characters.rp_yesterday,
        date_part('epoch'::text, guild_characters.joined_at) AS joined_at_epoch
    FROM
        guild_characters
    LEFT JOIN
        characters ON guild_characters.character_id = characters.id
    LEFT JOIN
        guilds ON guild_characters.guild_id = guilds.id
    JOIN
        users ON characters.user_id = users.id
    LEFT JOIN
        discord ON users.id = discord.user_id
    ORDER BY
        guild_characters.guild_id,
        guild_characters.order_index;
    """

    __tablename__ = "guild_characters_by_id"
    id: Mapped[int] = mapped_column(primary_key=True)
    guild_id: Mapped[int]
    guild_name: Mapped[str] = mapped_column(VARCHAR(24))
    uid: Mapped[int]
    psn_id: Mapped[str]
    discord_id: Mapped[str] = mapped_column(VARCHAR(21))
    character_id: Mapped[int]
    character_name: Mapped[str]
    weapon_type: Mapped[int] = mapped_column(nullable=True)
    gr: Mapped[int] = mapped_column(nullable=True)
    hr: Mapped[int] = mapped_column(nullable=True)
    gcp: Mapped[int] = mapped_column(nullable=True)
    kouryou_point: Mapped[int] = mapped_column(nullable=True)
    netcafe_points: Mapped[int] = mapped_column(nullable=True)
    promo_points: Mapped[int]
    daily_quests: Mapped[int]
    bonus_quests: Mapped[int]
    last_login: Mapped[int] = mapped_column(nullable=True)
    order_index: Mapped[int]
    avoid_leadership: Mapped[bool]
    daily_time: Mapped[float]
    joined_at_epoch: Mapped[float]
