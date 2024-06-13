"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class RengokuScore(Base):
    """Rengoku Score table object"""
    __tablename__ = "rengoku_score"
    id: Mapped[int] = mapped_column(primary_key=True)
