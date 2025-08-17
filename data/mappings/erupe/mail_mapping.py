"""Table mappings module"""
import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import (
    VARCHAR,
    TIMESTAMP
)

from ..base_mapping import Base

class Mail(Base):
    """Mail table object"""
    __tablename__ = "mail"
    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(nullable=False)
    recipient_id: Mapped[int] = mapped_column(nullable=False)
    subject: Mapped[str] = mapped_column(VARCHAR())
    body: Mapped[str] = mapped_column(VARCHAR())
    read: Mapped[bool] = mapped_column(nullable=False)
    attached_item_received: Mapped[bool] = mapped_column(nullable=False)
    attached_item: Mapped[int] = mapped_column(nullable=True)
    attached_item_amount: Mapped[int] = mapped_column(nullable=False)
    is_guild_invite: Mapped[bool] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now()) # pylint: disable=[not-callable]
    deleted: Mapped[bool] = mapped_column(nullable=False)
    locked: Mapped[bool] = mapped_column(nullable=False)
    is_sys_message: Mapped[bool] = mapped_column(nullable=False)
    sender_name: Mapped[str] = mapped_column(VARCHAR())
