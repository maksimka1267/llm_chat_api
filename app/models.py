import uuid
import decimal
import datetime as dt

from sqlalchemy import (
    Column, String, DateTime, Integer, Numeric,
    ForeignKey, Text
)
from sqlalchemy.orm import relationship

from .database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    total_prompt_tokens = Column(Integer, default=0)
    total_completion_tokens = Column(Integer, default=0)
    total_cost_usd = Column(Numeric(12, 6), default=decimal.Decimal("0"))

    messages = relationship(
        "Message",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"))
    role = Column(String, nullable=False)  # "user" или "assistant"
    content = Column(Text, nullable=False)

    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    cost_usd = Column(Numeric(12, 6), nullable=True)

    created_at = Column(DateTime, default=dt.datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")
