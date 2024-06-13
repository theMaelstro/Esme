"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class GachaItems(Base):
    """Gacha Items table object"""
    __tablename__ = "gacha_items"
