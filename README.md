# Claude Chat API

A small FastAPI backend for chatting with the Claude API (Anthropic), with both
a plain JSON endpoint and a streaming (SSE) endpoint, plus a minimal web UI for
manual testing.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY
```

## Run

```bash
uvicorn app.main:app --reload
```

Open http://localhost:8000 for the test chat UI, or use the API directly.

## API

### `POST /api/chat` — single response

```bash
curl http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello, Claude"}]
  }'
```

Response:

```json
{
  "role": "assistant",
  "content": "Hello! How can I help you today?",
  "model": "claude-opus-4-8",
  "stop_reason": "end_turn",
  "input_tokens": 10,
  "output_tokens": 12
}
```

### `POST /api/chat/stream` — Server-Sent Events

Same request body; the response is an SSE stream of text deltas:

```
data: {"text": "Hello"}

data: {"text": "! How"}

...

event: done
data: {}
```

### Request body (both endpoints)

```json
{
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "system": "optional system prompt",
  "model": "optional override, defaults to CLAUDE_MODEL",
  "max_tokens": 4096
}
```

The API is stateless — the client is responsible for sending the full
conversation history (`messages`) on every request, alternating `user` and
`assistant` turns starting with `user`. The bundled UI (`static/index.html`)
does this for you.

## Configuration

Set via `.env` or environment variables:

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | required, your Anthropic API key |
| `CLAUDE_MODEL` | `claude-opus-4-8` | model ID used unless overridden per-request |
| `MAX_TOKENS` | `4096` | default max output tokens |

Other current model IDs: `claude-sonnet-5`, `claude-haiku-4-5`.
