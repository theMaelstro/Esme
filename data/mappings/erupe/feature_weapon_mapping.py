"""Table mappings module"""
import datetime

from sqlalchemy import (
    func,
    Column,
    String
)
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class FeatureWeapon(Base):
    """Feature Weapon table object"""
    __tablename__ = "feature_weapon"
    start_time: Mapped[datetime.datetime] = mapped_column(
        primary_key=True,
        nullable=True,
        server_default=func.now() # pylint: disable=[not-callable]
    )
    featured: Mapped[int]
