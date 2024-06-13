"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class UserBinary(Base):
    """User Binary table object"""
    __tablename__ = "user_binary"
