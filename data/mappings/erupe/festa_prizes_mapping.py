"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class FestaPrizes(Base):
    """Festa Prizes table object"""
    __tablename__ = "festa_prizes"
    id: Mapped[int] = mapped_column(primary_key=True)
