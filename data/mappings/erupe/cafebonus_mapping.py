"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import Sequence

from ..base_mapping import Base

class CafeBonus(Base):
    """Cafe Bonus table object"""
    __tablename__ = "cafebonus"
    id: Mapped[int] = mapped_column(primary_key=True, default=Sequence('cafebonus_id_seq').next_value())
    time_req: Mapped[int]
    item_type: Mapped[int]
    item_id: Mapped[int]
    quantity: Mapped[int]
