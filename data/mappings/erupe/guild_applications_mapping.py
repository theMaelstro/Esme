"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class GuildApplications(Base):
    """Guild Applications table object"""
    __tablename__ = "guild_applications"
    id: Mapped[int] = mapped_column(primary_key=True)
    guild_id: Mapped[int]
    character_id: Mapped[int]
    actor_id: Mapped[int]
