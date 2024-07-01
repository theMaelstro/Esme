"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import (
    VARCHAR
)

from ...base_mapping import Base

class GuildApplicationsDetails(Base):
    """Guild Characters by Guild Id view object"""

    __query__ = """
    CREATE OR REPLACE VIEW guild_applications_details AS
    SELECT 
        guild_applications.id,
        guilds.name as guild_name,
        t1.name as initiate_name,
        guild_applications.actor_id,
        t2.name as progenitor_name,
        round(date_part('epoch'::text, guild_applications.created_at)) AS applied_on
    FROM 
        guild_applications
    LEFT JOIN 
        characters t1 ON guild_applications.character_id = t1.id
    LEFT JOIN 
        characters t2 ON guild_applications.actor_id = t2.id
    LEFT JOIN
        guilds ON guild_applications.guild_id = guilds.id
    ORDER BY
        guild_applications.id;
    """
    __tablename__ = "guild_applications_details"
    id: Mapped[int] = mapped_column(primary_key=True)
    guild_name: Mapped[str] = mapped_column(VARCHAR(24))
    initiate_name: Mapped[str] = mapped_column(VARCHAR(15))
    progenitor_name: Mapped[str] = mapped_column(VARCHAR(15))
    applied_on: Mapped[float]
