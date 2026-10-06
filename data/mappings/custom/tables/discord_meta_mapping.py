"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import (
    TEXT,
    JSON
)

from data.mappings import Base

class DiscordMeta(Base):
    """Discord Meta table object"""
    __tablename__ = "discord_meta"
    key: Mapped[str] = mapped_column(TEXT, primary_key=True)
    data: Mapped[JSON] = mapped_column(JSON)
