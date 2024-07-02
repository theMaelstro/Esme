"""Table mappings module"""
import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import (
    TIMESTAMP,
)

from ..base_mapping import Base

class Events(Base):
    """Events table object"""
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str]
    start_time: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(), # pylint: disable=[not-callable]
        nullable=True
    )
