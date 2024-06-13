"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class Achievements(Base):
    """Achievements table object"""
    __tablename__ = "achievements"
    id: Mapped[int] = mapped_column(primary_key=True)
