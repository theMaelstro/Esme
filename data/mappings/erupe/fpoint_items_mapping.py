"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class FestaPointsItems(Base):
    """Festa Points Items table object"""
    __tablename__ = "fpoint_items"
