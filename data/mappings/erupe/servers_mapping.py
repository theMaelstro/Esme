"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import (
    VARCHAR
)

from ..base_mapping import Base

class Servers(Base):
    """Servers table object"""
    __tablename__ = "servers"
    server_id: Mapped[int] = mapped_column(primary_key=True)
    current_players: Mapped[int]
    world_name: Mapped[str] = mapped_column(VARCHAR(15))
    world_description: Mapped[str] = mapped_column(VARCHAR(15))
    land: Mapped[int]
