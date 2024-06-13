"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class DistributionItems(Base):
    """Distribution Items table object"""
    __tablename__ = "distribution_items"
