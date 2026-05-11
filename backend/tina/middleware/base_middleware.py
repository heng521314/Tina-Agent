from typing import Any, Callable
from langchain.agents.middleware import (
    dynamic_prompt, ModelRequest, ModelResponse, before_model, Runtime, AgentState, wrap_model_call
)
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langchain.messages import RemoveMessage
from backend.tina.tools import web_search
import logging

logger = logging.getLogger(__name__)


# 动态传递提示词
@dynamic_prompt
def dynamic_prompt(request: ModelRequest):
    # 获取传递上下文
    llm_role = request.runtime.context.get("mode", "plan")
    prompt = "You are tina a useful assistant."
    # 计划模式
    if llm_role == "plan":
        return f"""{prompt}, 你的任务是判断当前任务是否需要制作一个计划，如果用户问的问题简单，如用户向你打招呼，你直接回答就行，由你自己判断是否需要制作计划
        你制作计划时需要遵循以下这几个要点：
        1.先思考，不要立即动手写
        2.保持计划简洁性，易用性
        3.制定计划时不要说废话，只说与用户问题最相关的
        """
    elif llm_role == "build":
        return f"""{prompt}，你可以根据用户已经设计好的计划，解决问题，当用户没有提供计划时，你必须先思考再制定计划，再执行
        你可以调用任何对你有帮助的工具
        """
    return prompt


@wrap_model_call
def interceptor_tool(request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]):
    mode = request.runtime.context['mode']
    tools: list = request.tools
    if mode == "plan":
        return handler(request.override(tools=[web_search]))
    return handler(request.override(tools=tools))


@before_model
def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Keep only the last few messages to fit context window."""
    messages = state["messages"]

    if len(messages) > 3:
        return None  # No changes needed

    first_msg = messages[0]
    recent_messages = messages[-3:] if len(messages) % 2 == 0 else messages[-4:]
    new_messages = [first_msg] + recent_messages

    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *new_messages
        ]
    }
