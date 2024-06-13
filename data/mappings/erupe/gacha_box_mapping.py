"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class GachaBox(Base):
    """Gacha Box table object"""
    __tablename__ = "gacha_box"
