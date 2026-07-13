import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from anthropic import APIStatusError, APIConnectionError

from app.claude_service import send_message, stream_message
from app.schemas import ChatRequest, ChatResponse

app = FastAPI(title="Claude Chat API")


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        return await send_message(
            messages=request.messages,
            system=request.system,
            model=request.model,
            max_tokens=request.max_tokens,
        )
    except APIConnectionError:
        raise HTTPException(status_code=502, detail="Could not reach the Claude API")
    except APIStatusError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    async def event_source():
        try:
            async for text in stream_message(
                messages=request.messages,
                system=request.system,
                model=request.model,
                max_tokens=request.max_tokens,
            ):
                yield f"data: {json.dumps({'text': text})}\n\n"
            yield "event: done\ndata: {}\n\n"
        except APIConnectionError:
            yield f"event: error\ndata: {json.dumps({'error': 'Could not reach the Claude API'})}\n\n"
        except APIStatusError as e:
            yield f"event: error\ndata: {json.dumps({'error': e.message})}\n\n"

    return StreamingResponse(event_source(), media_type="text/event-stream")


app.mount("/", StaticFiles(directory="static", html=True), name="static")
