from collections.abc import AsyncIterator
from functools import lru_cache

import anthropic

from app.config import get_settings
from app.schemas import ChatMessage, ChatResponse


@lru_cache
def get_client() -> anthropic.AsyncAnthropic:
    settings = get_settings()
    return anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


def _to_api_messages(messages: list[ChatMessage]) -> list[dict]:
    return [{"role": m.role, "content": m.content} for m in messages]


async def send_message(
    messages: list[ChatMessage],
    system: str | None = None,
    model: str | None = None,
    max_tokens: int | None = None,
) -> ChatResponse:
    settings = get_settings()
    client = get_client()

    response = await client.messages.create(
        model=model or settings.claude_model,
        max_tokens=max_tokens or settings.max_tokens,
        system=system,
        messages=_to_api_messages(messages),
    )

    text = "".join(block.text for block in response.content if block.type == "text")

    return ChatResponse(
        content=text,
        model=response.model,
        stop_reason=response.stop_reason,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )


async def stream_message(
    messages: list[ChatMessage],
    system: str | None = None,
    model: str | None = None,
    max_tokens: int | None = None,
) -> AsyncIterator[str]:
    """Yields raw text deltas as they arrive from Claude."""
    settings = get_settings()
    client = get_client()

    async with client.messages.stream(
        model=model or settings.claude_model,
        max_tokens=max_tokens or settings.max_tokens,
        system=system,
        messages=_to_api_messages(messages),
    ) as stream:
        async for text in stream.text_stream:
            yield text
