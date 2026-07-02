"""Persistence maintains sessions middleware"""

from typing import Any, Final
from langgraph.runtime import Runtime
from langchain.agents.middleware import AgentMiddleware, AgentState
from backend.tina.store.mongo_store_base import MongoDBStoreBase

store = MongoDBStoreBase()
COLLECTION_SUFFIX: Final[str] = "message"


class SessionState(AgentState):
    pass


class SessionMiddleware(AgentMiddleware[SessionState]):
    state_schema = SessionState

    def save_session(self, id: str, msg: str, role: str):
        data = {"session_id": id, "role": role, "content": msg}
        store.save_one(COLLECTION_SUFFIX, data)

    """Each time the agent is called before execution, it is called only once."""

    def before_agent(
        self, state: SessionState, runtime: Runtime
    ) -> dict[str, Any] | None:
        user_msg = state["messages"][-1].content
        session_id = runtime.context["thread_id"]
        if user_msg:
            return self.save_session(id=session_id, msg=user_msg, role="user")
        return None

    """It is executed after each agent call, and only called once."""

    def after_agent(
        self, state: SessionState, runtime: Runtime
    ) -> dict[str, Any] | None:
        last_msg = state["messages"][-1].content
        session_id = runtime.context["thread_id"]
        if last_msg:
            return self.save_session(id=session_id, msg=last_msg, role="ai")
        return None
