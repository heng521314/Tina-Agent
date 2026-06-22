import logging
from typing import Any, Callable
from langchain.agents.middleware import (
    dynamic_prompt,
    ModelRequest,
    ModelResponse,
    before_model,
    Runtime,
    AgentState,
    wrap_model_call,
)
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langchain.messages import RemoveMessage
from backend.tina.config import get_skills_prompt_section
from backend.tina.tools import get_all_tool, web_search, load_skill, glob

logger = logging.getLogger(__name__)


# 动态传递提示词
@dynamic_prompt
def dynamic_prompt(request: ModelRequest):
    # 获取传递上下文
    llm_role = request.runtime.context.get("mode", "plan")
    skill_prompt = get_skills_prompt_section()
    tools = ", ".join([tool.name for tool in get_all_tool()])
    prompt = f"""
You are an agent assistant for Tina. You need to use the provided tools and skills to complete the user’s tasks. After receiving the task, do not respond immediately; instead, think first and create an execution plan. When making the plan, strictly follow the following requirements:  
1. Prioritize checking the provided skills. Determine whether any available skill package exists based on the description of the skills. Even if there’s a 1% chance that the skill matches the user’s problem, you must use the `load_skill` tool to load the skill and guide your actions.  
2. If you have any doubts, ask the user for clarification. Then, implement the plan step by step until the task is completed.  
The following are the available skill systems.
{skill_prompt}
available tool
{tools}
"""
    return prompt


@wrap_model_call
def interceptor_tool(
    request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]
):
    """interceptor tool"""
    mode = request.runtime.context["mode"]
    tools: list = request.tools
    if mode == "plan":
        return handler(request.override(tools=[web_search, load_skill, glob]))
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

    return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *new_messages]}
