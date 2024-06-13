"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class Distribution(Base):
    """Distribution table object"""
    __tablename__ = "distribution"
    id: Mapped[int] = mapped_column(primary_key=True)
