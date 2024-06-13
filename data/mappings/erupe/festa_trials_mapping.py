"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class FestaTrials(Base):
    """Festa Trials table object"""
    __tablename__ = "festa_trials"
    id: Mapped[int] = mapped_column(primary_key=True)
    objective: Mapped[int]
    goal_id: Mapped[int]
    times_req: Mapped[int]
    locale_req: Mapped[int]
    reward: Mapped[int]