"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class ShopItemsBought(Base):
    """Shop Items Bought table object"""
    __tablename__ = "shop_items_bought"
    id: Mapped[int] = mapped_column(primary_key=True)
