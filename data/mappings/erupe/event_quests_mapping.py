"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class EventQuests(Base):
    """Event Quests table object"""
    __tablename__ = "event_quests"
    id: Mapped[int] = mapped_column(primary_key=True)
