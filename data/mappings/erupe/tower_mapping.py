"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class Tower(Base):
    """Tower table object"""
    __tablename__ = "tower"
    id: Mapped[int] = mapped_column(primary_key=True)
