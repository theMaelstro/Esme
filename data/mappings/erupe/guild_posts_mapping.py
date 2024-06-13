"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class GuildPosts(Base):
    """Guild Posts table object"""
    __tablename__ = "guild_posts"
    id: Mapped[int] = mapped_column(primary_key=True)
