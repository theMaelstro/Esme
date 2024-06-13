"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class GuildAlliances(Base):
    """Guild Alliances table object"""
    __tablename__ = "guild_alliances"
    id: Mapped[int] = mapped_column(primary_key=True)
