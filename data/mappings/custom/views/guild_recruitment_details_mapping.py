"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy.dialects.postgresql import (
    VARCHAR
)

from ...base_mapping import Base

class GuildRecruitmentDetails(Base):
    """Guild Recruitment Details view object"""

    __query__ = """
    CREATE OR REPLACE VIEW guild_recruitment_details AS
    SELECT
        guilds.id as guild_id,
        guilds.name as guild_name,
        guilds.rank_rp as guild_rp,
        characters.name as leader_name,
        guilds.recruiting,
        discord.discord_id,
        x.members
    FROM
        guilds
    INNER JOIN characters ON guilds.leader_id = characters.id
    LEFT JOIN (
        SELECT guild_id, COUNT(*)::int as members
        FROM guild_characters
        GROUP BY guild_id
    ) x ON x.guild_id = guilds.id
    LEFT JOIN discord ON guilds.leader_id = discord.character_id
    WHERE recruiting IS True
    AND (
        members > 0
        AND members < 90
    )
    ORDER BY members DESC;
    """

    __tablename__ = "guild_recruitment_details"
    guild_id: Mapped[int] = mapped_column(primary_key=True)
    guild_name: Mapped[str] = mapped_column(VARCHAR(24))
    guild_rp: Mapped[int]
    leader_name: Mapped[str] = mapped_column(VARCHAR(15))
    recruiting: Mapped[bool]
    discord_id: Mapped[str] = mapped_column(VARCHAR(21))
    members: Mapped[int]
