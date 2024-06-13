"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class SignSessions(Base):
    """Sign Sessions table object"""
    __tablename__ = "sign_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
