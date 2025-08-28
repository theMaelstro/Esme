"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy.dialects.postgresql import (
    VARCHAR
)

from ...base_mapping import Base

class CharacterDetails(Base):
    """Character Details view object"""

    __query__ = """
    CREATE OR REPLACE VIEW character_details AS
    SELECT 
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
        g.guild_id,
        guilds.name AS guild_name,
        g.order_index,
        date_part('epoch'::text, g.joined_at) AS joined_at_epoch,
        users.id AS uid,
        users.psn_id,
        discord.discord_id,
        discord.character_id as cid
    FROM characters
        LEFT JOIN guild_characters g ON characters.id = g.character_id
        LEFT JOIN guilds ON guilds.id = g.guild_id
        JOIN users ON users.id = characters.user_id
        LEFT JOIN discord ON users.id = discord.user_id
    ORDER BY characters.id;
    """

    __tablename__ = "character_details"
    character_id: Mapped[int] = mapped_column(primary_key=True)
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
    daily_time: Mapped[float]
    guild_id: Mapped[int]
    guild_name: Mapped[str] = mapped_column(VARCHAR(24))
    order_index: Mapped[int]
    joined_at_epoch: Mapped[float]
    uid: Mapped[int]
    psn_id: Mapped[str]
    discord_id: Mapped[str] = mapped_column(VARCHAR(21))
    cid: Mapped[int]
