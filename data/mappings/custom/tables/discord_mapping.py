"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import (
    VARCHAR,
    TEXT
)

from data.mappings import Base

class Discord(Base):
    """Discord table object"""
    __tablename__ = "discord"
    id: Mapped[int] = mapped_column(primary_key=True)
    discord_id: Mapped[str] = mapped_column(VARCHAR(21))
    terms: Mapped[str] = mapped_column(TEXT, nullable=True)
    user_id: Mapped[int] = mapped_column(nullable=True)
    character_id: Mapped[int] = mapped_column(nullable=True)
    cd_backup: Mapped[int] = mapped_column(nullable=True)
