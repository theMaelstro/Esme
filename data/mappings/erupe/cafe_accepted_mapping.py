"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class CafeAccepted(Base):
    """Cafe Accepted table object"""
    __tablename__ = "cafe_accepted"
    cafe_id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int]

