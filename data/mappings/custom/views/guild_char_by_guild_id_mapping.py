"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ...base_mapping import Base

class GuildCharactersByGuildId(Base):
    """Guild Characters by Guild Id view object"""

    __query__ = """
    CREATE OR REPLACE VIEW guild_characters_by_id AS
    SELECT
        guild_characters.id,
        guild_characters.guild_id,
        characters.name,
        guild_characters.order_index,
        date_part('epoch'::text, guild_characters.joined_at) AS joined_at_epoch
    FROM guild_characters
    LEFT JOIN characters 
    ON guild_characters.character_id = characters.id
    ORDER BY guild_characters.guild_id, guild_characters.order_index;
    """
    __tablename__ = "guild_characters_by_id"
    id: Mapped[int] = mapped_column(primary_key=True)
    guild_id: Mapped[int]
    name: Mapped[str]
    order_index: Mapped[int]
    joined_at_epoch: Mapped[float]
