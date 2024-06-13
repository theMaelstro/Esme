"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class KillLogs(Base):
    """Kill Logs table object"""
    __tablename__ = "kill_logs"
