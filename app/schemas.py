from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["user", "assistant"]


class ChatMessage(BaseModel):
    role: Role
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1)
    system: str | None = None
    model: str | None = None
    max_tokens: int | None = None


class ChatResponse(BaseModel):
    role: Literal["assistant"] = "assistant"
    content: str
    model: str
    stop_reason: str | None
    input_tokens: int
    output_tokens: int
