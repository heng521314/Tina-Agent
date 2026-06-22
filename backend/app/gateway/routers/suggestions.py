"""根据最近聊天记录生成个性化建议"""

import logging
from fastapi import APIRouter
from pydantic import BaseModel, Field
from backend.tina.models.base_factory import create_chat_model

default: list[str] = [
    "有什么可以帮你的吗",
    "你今天过得怎样",
    "好久不见",
]

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/{thread_id}", tags=["suggestions"])


class SuggestionMessage(BaseModel):
    role: str = Field(description="user role")
    content: str = Field(description="human or ai message")


class SuggestionRequest(BaseModel):
    messages: list[SuggestionMessage]
    N: int = Field(
        default=3, ge=1, le=5, description="number of suggestion to generate"
    )


class SuggestionResponse(BaseModel):
    suggestions: list[str]


def _format_message(messages: list[SuggestionMessage]):
    parts: list[str] = []
    for m in messages:
        role = m.role.strip().lower()
        if role in ("human", "user"):
            parts.append(f"User: {m.content.strip()}")
        elif role in ("ai", "assistant"):
            parts.append(f"AI: {m.content.strip()}")
        else:
            parts.append(f"{role}: {m.content.strip()}")
    return "\n".join(parts).strip()


@router.post("/suggestions", response_model=SuggestionResponse)
async def generate_suggestion(request: SuggestionRequest) -> SuggestionResponse:
    """
    根据用户最近的聊天生成建议
    args:
        messages: user chat message
        N: number of suggestion to generate
    request:
    {
      "messages":[{"role":"user","content":"我喜欢打游戏"}, {"role":"ai","content":"你喜欢打什么游戏，可以给我分享一下吗😄"}],
      "N":3
    }
    response:
    {
      "suggestions": [
        "你最喜欢玩的游戏是什么类型呢？",
        "有没有特别喜欢的游戏角色或者剧情？",
        "你平时会和朋友一起联机打游戏吗？"
      ]
    }
    """
    if len(request.messages) == 0:
        return SuggestionResponse(suggestions=default)

    N = request.N
    logger.info("user message: ", request.messages)
    # 查询数据库获得最近聊天信息
    messages = _format_message(request.messages)
    # 发送给大模型生产建议
    prompt = (
        "You are generating follow-up questions to help the user continue the conversation.\n"
        f"Based on the conversation below, produce EXACTLY {N} short questions the user might ask next.\n"
        "Requirements:\n"
        "- Questions must be relevant to the conversation.\n"
        "- Questions must be written in the same language as the user.\n"
        "- Keep each question concise (ideally <= 20 words / <= 40 Chinese characters).\n"
        "- Do NOT include numbering, markdown, or any extra text.\n"
        "Conversation:\n"
        f"{messages}\n"
    )
    suggestion_list: list[str] = []
    llm = create_chat_model()
    llm_resp = llm.invoke("".join(prompt))
    for c in llm_resp.content.split("\n"):
        suggestion_list.append(c)

    return SuggestionResponse(suggestions=suggestion_list)
