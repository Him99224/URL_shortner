from datetime import datetime,timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class URL(Base):
    __tablename__="urls"

    id:Mapped[int]= mapped_column(
        Integer,
        primary_key=True
    )

    original_url:Mapped[str]=mapped_column(
        String,
        nullable=False
    )

    short_code:Mapped[str]=mapped_column(
        String(10),
        unique=True,
        nullable=True
    )

    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    expires_at:Mapped[datetime| None]=mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    click_count:Mapped[int]=mapped_column(
        Integer,
        default=0
    )