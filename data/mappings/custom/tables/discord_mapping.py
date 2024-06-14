"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import (
    VARCHAR
)

from ...base_mapping import Base

class Discord(Base):
    """Discord table object"""
    __tablename__ = "discord"
    id: Mapped[int] = mapped_column(primary_key=True)
    discord_id: Mapped[str] = mapped_column(VARCHAR(18))
    user_id: Mapped[int]
    character_id: Mapped[int]
