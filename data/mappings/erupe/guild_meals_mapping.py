"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class GuildMeals(Base):
    """Guild Meals table object"""
    __tablename__ = "guild_meals"
    id: Mapped[int] = mapped_column(primary_key=True)
