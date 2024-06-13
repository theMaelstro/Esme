"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class FeatureWeapon(Base):
    """Feature Weapon table object"""
    __tablename__ = "feature_weapon"
    id: Mapped[int] = mapped_column(primary_key=True)
