import datetime as dt
import decimal
from typing import List, Optional

from pydantic import BaseModel


class StartSessionResponse(BaseModel):
    session_id: str
    created_at: dt.datetime


class SendMessageRequest(BaseModel):
    message: str


class MessageDTO(BaseModel):
    role: str
    content: str
    created_at: dt.datetime
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    cost_usd: Optional[decimal.Decimal] = None

    class Config:
        from_attributes = True


class SendMessageResponse(BaseModel):
    reply: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    message_cost_usd: decimal.Decimal
    session_total_cost_usd: decimal.Decimal


class SessionHistoryResponse(BaseModel):
    session_id: str
    created_at: dt.datetime
    total_prompt_tokens: int
    total_completion_tokens: int
    total_cost_usd: decimal.Decimal
    messages: List[MessageDTO]
