"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class Achievements(Base):
    """Achievements table object"""
    __tablename__ = "achievements"
    id: Mapped[int] = mapped_column(primary_key=True)
    ach0: Mapped[int] = mapped_column(nullable=True)
    ach1: Mapped[int] = mapped_column(nullable=True)
    ach2: Mapped[int] = mapped_column(nullable=True)
    ach3: Mapped[int] = mapped_column(nullable=True)
    ach4: Mapped[int] = mapped_column(nullable=True)
    ach5: Mapped[int] = mapped_column(nullable=True)
    ach6: Mapped[int] = mapped_column(nullable=True)
    ach7: Mapped[int] = mapped_column(nullable=True)
    ach8: Mapped[int] = mapped_column(nullable=True)
    ach9: Mapped[int] = mapped_column(nullable=True)
    ach10: Mapped[int] = mapped_column(nullable=True)
    ach11: Mapped[int] = mapped_column(nullable=True)
    ach12: Mapped[int] = mapped_column(nullable=True)
    ach13: Mapped[int] = mapped_column(nullable=True)
    ach14: Mapped[int] = mapped_column(nullable=True)
    ach15: Mapped[int] = mapped_column(nullable=True)
    ach16: Mapped[int] = mapped_column(nullable=True)
    ach17: Mapped[int] = mapped_column(nullable=True)
    ach18: Mapped[int] = mapped_column(nullable=True)
    ach19: Mapped[int] = mapped_column(nullable=True)
    ach20: Mapped[int] = mapped_column(nullable=True)
    ach21: Mapped[int] = mapped_column(nullable=True)
    ach22: Mapped[int] = mapped_column(nullable=True)
    ach23: Mapped[int] = mapped_column(nullable=True)
    ach24: Mapped[int] = mapped_column(nullable=True)
    ach25: Mapped[int] = mapped_column(nullable=True)
    ach26: Mapped[int] = mapped_column(nullable=True)
    ach27: Mapped[int] = mapped_column(nullable=True)
    ach28: Mapped[int] = mapped_column(nullable=True)
    ach29: Mapped[int] = mapped_column(nullable=True)
    ach30: Mapped[int] = mapped_column(nullable=True)
    ach31: Mapped[int] = mapped_column(nullable=True)
    ach32: Mapped[int] = mapped_column(nullable=True)
