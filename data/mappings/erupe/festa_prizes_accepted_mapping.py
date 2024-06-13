"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class FestaPrizesAccepted(Base):
    """Festa Prizes Accepted table object"""
    __tablename__ = "festa_prizes_accepted"
