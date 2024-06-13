"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class Stamps(Base):
    """Stamps table object"""
    __tablename__ = "stamps"
