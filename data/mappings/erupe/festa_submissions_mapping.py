"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class FestaSubmissions(Base):
    """Festa Submissions table object"""
    __tablename__ = "festa_submissions"
