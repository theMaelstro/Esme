"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class LoginBoost(Base):
    """Login Boost table object"""
    __tablename__ = "login_boost"
