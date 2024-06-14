"""Table mappings module"""
import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class Bans(Base):
    """Bans table object"""
    __tablename__ = "bans"
    id: Mapped[int] = mapped_column(primary_key=True)
    expires: Mapped[datetime.datetime] = mapped_column(nullable=True, server_default=func.now()) # pylint: disable=[not-callable]
