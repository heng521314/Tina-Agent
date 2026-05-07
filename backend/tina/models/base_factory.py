"""模型工厂"""
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from backend.tina.config.model_config import parse_model_config
from backend.tina.tools.base_tools import get_all_tool

# get all tools
tool_list = get_all_tool()


def create_chat_model() -> ChatOpenAI:
    config = parse_model_config()['env']
    llm = ChatOpenAI(
        **config
    )
    return llm


def create_custom_agent():
    llm = create_chat_model()
    agent = create_agent(
        model=llm,
        tools=[*tool_list],
        middleware=[],
        system_prompt="""You are tina a useful assistant."""
    )
    return agent
