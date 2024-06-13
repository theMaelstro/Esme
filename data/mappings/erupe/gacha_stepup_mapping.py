"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class GachaStepUp(Base):
    """Gacha Step Up table object"""
    __tablename__ = "gacha_stepup"
