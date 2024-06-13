"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class GuildHunts(Base):
    """Guild Hunts table object"""
    __tablename__ = "guild_hunts"
