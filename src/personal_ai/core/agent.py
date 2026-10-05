from collections.abc import Callable
from typing import Protocol

from personal_ai.core.conversation_session import ConversationSession
from personal_ai.core.executor import Executor
from personal_ai.core.llm import ChatMessage
from personal_ai.core.llm_integration import LLMIntegration
from personal_ai.core.planner import Planner
from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.retrieval.local import RetrievalRequest, RetrievalResult
from personal_ai.tools.executor import ToolExecutor
from personal_ai.tools.model import ToolResult
from personal_ai.tools.tool import Tool


class RetrievalCapability(Protocol):
    """Canonical retrieval capability supplied to the agent."""

    def retrieve(
        self,
        request: RetrievalRequest,
    ) -> list[RetrievalResult]:
        ...


class Agent:
    def __init__(
        self,
        integration: LLMIntegration,
        retriever: Callable[[str], list[str]] | None = None,
        planner: Planner | None = None,
        executor: Executor | None = None,
        retrieval: RetrievalCapability | None = None,
    ) -> None:
        if (planner is None) != (executor is None):
            raise ValueError("planner and executor must be provided together")

        self.integration = integration
        self.retriever = retriever
        self.planner = planner
        self.executor = executor
        self.retrieval = retrieval

    def run(
        self,
        user_request: str,
        session: ConversationSession,
    ) -> str:
        if not isinstance(user_request, str):
            raise ValueError("user_request must be a string")

        if self.planner is None:
            return self._respond(user_request, session)

        plan = self.planner.plan(user_request)

        response_executor = self.executor.with_capabilities(
            {
                "respond": lambda value: self._respond(
                    value,
                    session,
                ),
            }
        )

        results = response_executor.execute(plan)

        if len(results) != 1:
            raise ValueError("agent execution produced an unexpected result count")

        result = results[0]

        if not isinstance(result, str):
            raise ValueError("agent response capability returned a non-string result")

        return result

    def _respond(
        self,
        user_request: str,
        session: ConversationSession,
    ) -> str:
        user_message = ChatMessage(
            role="user",
            content=user_request,
        )

        session.add_message(user_message)

        if self.retrieval is not None:
            retrieval_results = self.retrieval.retrieve(
                RetrievalRequest(query=user_request)
            )

            if not isinstance(retrieval_results, list):
                raise ValueError(
                    "retrieval capability must return a list"
                )

            for result in retrieval_results:
                if not isinstance(result, RetrievalResult):
                    raise ValueError(
                        "retrieval capability returned an invalid result"
                    )


        if self.retriever is not None:
            contexts = self.retriever(user_request)

            for context in contexts:
                session.add_message(
                    ChatMessage(
                        role="system",
                        content=f"Retrieved context:\n{context}",
                    )
                )

        response = self.integration.generate(session)

        return response.text

    def execute_tool(
        self,
        tool: Tool,
        executor: ToolExecutor,
        input_data: object,
        permission_evaluator: PermissionEvaluator,
    ) -> ToolResult:
        return executor.execute(
            tool=tool,
            input_data=input_data,
            permission_evaluator=permission_evaluator,
        )
