"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ...base_mapping import Base

class Servers(Base):
    """Servers table object"""
    __tablename__ = "servers"
