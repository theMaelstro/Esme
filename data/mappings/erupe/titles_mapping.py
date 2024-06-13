"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class Titles(Base):
    """Titles table object"""
    __tablename__ = "titles"
    id: Mapped[int] = mapped_column(primary_key=True)
