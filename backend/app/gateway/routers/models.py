from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from typing import Any, Generator
from backend.tina.models.base_factory import create_custom_agent
from uuid import uuid4

router = APIRouter(prefix="/api", tags=['models'])


class ChatRequest(BaseModel):
    thread_id: str = Field(description="thread id")
    model: str = Field(description="model name")
    message: str = Field(description="user input")


class StreamEvent(BaseModel):
    type: str
    data: dict[str, Any] = Field(default_factory=dict)


def _extract_text(content) -> str:
    """Extract plain text from AIMessage content (str or list of blocks).

    String chunks are concatenated without separators to avoid corrupting
    token/character deltas or chunked JSON payloads. Dict-based text blocks
    are treated as full text blocks and joined with newlines to preserve
    readability.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        if content and all(isinstance(block, str) for block in content):
            chunk_like = len(content) > 1 and all(
                isinstance(block, str)
                and len(block) <= 20
                and any(ch in block for ch in '{}[]":,')
                for block in content
            )
            return "".join(content) if chunk_like else "\n".join(content)

        pieces: list[str] = []
        pending_str_parts: list[str] = []

        def flush_pending_str_parts() -> None:
            if pending_str_parts:
                pieces.append("".join(pending_str_parts))
                pending_str_parts.clear()

        for block in content:
            if isinstance(block, str):
                pending_str_parts.append(block)
            elif isinstance(block, dict):
                flush_pending_str_parts()
                text_val = block.get("text")
                if isinstance(text_val, str):
                    pieces.append(text_val)

        flush_pending_str_parts()
        return "\n".join(pieces) if pieces else ""
    return str(content)


@router.post(
    "/chat",
)
async def chat_message(
        request: ChatRequest
) -> Generator[StreamEvent, None, None]:
    """
    basic chat interface
    args:
        thread_id: 请求id
        model: 模型名称
        message: 用户输入
    response:
    {
      "type": "messages",
      "data": {
        "type": "ai",
        "content": "Hello! I'm doing well, thank you for asking. How about you? Is there anything you'd like to chat about or need help with today?",
        "id": "lc_run--019dfc82-d205-7800-b8d5-28f80f6bda17-0",
        "usage_metadata": {
          "input_tokens": 30,
          "output_tokens": 32,
          "total_tokens": 62
        }
      }
    }
    {
      "type": "end",
      "data": {
        "usage": {
          "input_tokens": 30,
          "output_tokens": 32,
          "total_tokens": 62
        }
      }
    }
    """
    if not request.thread_id:
        request.thread_id = str(uuid4())

    if not request.message:
        raise HTTPException(status_code=401, detail="message not empty")

    state = {"messages": [HumanMessage(request.message.strip())]}
    context = {"thread_id": request.thread_id}
    seen_ids: set[str] = set()
    cumulative_usage: dict[str, int] = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    agent = create_custom_agent()
    for chunk in agent.stream(state, context=context, stream_mode="values"):
        messages = chunk.get("messages", [])
        for msg in messages:
            msg_id = getattr(msg, "id", None)
            if msg_id and msg_id in seen_ids:
                continue
            if msg_id:
                seen_ids.add(msg_id)

            if isinstance(msg, AIMessage):
                # Track token usage from AI messages
                usage = getattr(msg, "usage_metadata", None)
                if usage:
                    cumulative_usage["input_tokens"] += usage.get("input_tokens", 0) or 0
                    cumulative_usage["output_tokens"] += usage.get("output_tokens", 0) or 0
                    cumulative_usage["total_tokens"] += usage.get("total_tokens", 0) or 0

                if msg.tool_calls:
                    yield StreamEvent(
                        type="messages",
                        data={
                            "type": "ai",
                            "content": "",
                            "id": msg_id,
                            "tool_calls": [{"name": tc["name"], "args": tc["args"], "id": tc.get("id")} for tc in
                                           msg.tool_calls],
                        },
                    )

                text = _extract_text(msg.content)
                if text:
                    event_data: dict[str, Any] = {"type": "ai", "content": text, "id": msg_id}
                    if usage:
                        event_data["usage_metadata"] = {
                            "input_tokens": usage.get("input_tokens", 0) or 0,
                            "output_tokens": usage.get("output_tokens", 0) or 0,
                            "total_tokens": usage.get("total_tokens", 0) or 0,
                        }
                    yield StreamEvent(type="messages", data=event_data)

            elif isinstance(msg, ToolMessage):
                yield StreamEvent(
                    type="messages",
                    data={
                        "type": "tool",
                        "content": _extract_text(msg.content),
                        "name": getattr(msg, "name", None),
                        "tool_call_id": getattr(msg, "tool_call_id", None),
                        "id": msg_id,
                    },
                )

    yield StreamEvent(type="end", data={"usage": cumulative_usage})
