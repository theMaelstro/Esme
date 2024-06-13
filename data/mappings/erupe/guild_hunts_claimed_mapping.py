"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class GuildHuntsClaimed(Base):
    """Guild Hunts Claimed table object"""
    __tablename__ = "guild_hunts_claimed"
