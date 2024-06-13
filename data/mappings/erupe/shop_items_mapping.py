"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class ShopItems(Base):
    """Shop Items table object"""
    __tablename__ = "shop_items"
