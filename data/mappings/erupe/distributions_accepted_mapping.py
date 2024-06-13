"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class DistributionsAccepted(Base):
    """Distributions Accepted table object"""
    __tablename__ = "distributions_accepted"
    id: Mapped[int] = mapped_column(primary_key=True)
