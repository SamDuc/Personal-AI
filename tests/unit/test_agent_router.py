import pytest

from personal_ai.core.agent_router import AgentRoute, AgentRouter
from personal_ai.core.conversation_session import ConversationSession


class StubAgent:
    def __init__(self, response: str) -> None:
        self.response = response
        self.requests: list[str] = []

    def run(
        self,
        user_request: str,
        session: ConversationSession,
    ) -> str:
        self.requests.append(user_request)
        return self.response


def test_router_resolves_registered_agent() -> None:
    agent = StubAgent("answer")
    router = AgentRouter(
        [AgentRoute(route_id="general", agent=agent)]
    )

    assert router.resolve("general") is agent


def test_router_rejects_unknown_route() -> None:
    router = AgentRouter([])

    with pytest.raises(ValueError, match="unknown agent route"):
        router.resolve("missing")


def test_router_rejects_duplicate_route() -> None:
    first = StubAgent("first")
    second = StubAgent("second")

    with pytest.raises(ValueError, match="duplicate route"):
        AgentRouter(
            [
                AgentRoute(route_id="general", agent=first),
                AgentRoute(route_id="general", agent=second),
            ]
        )


def test_router_preserves_user_request() -> None:
    agent = StubAgent("answer")
    router = AgentRouter(
        [AgentRoute(route_id="general", agent=agent)]
    )
    session = ConversationSession()

    request = "Find my project architecture notes."

    result = router.run(
        route_id="general",
        user_request=request,
        session=session,
    )

    assert result == "answer"
    assert agent.requests == [request]


def test_router_rejects_non_string_request() -> None:
    agent = StubAgent("answer")
    router = AgentRouter(
        [AgentRoute(route_id="general", agent=agent)]
    )

    with pytest.raises(ValueError, match="user_request must be a string"):
        router.run(
            route_id="general",
            user_request=123,
            session=ConversationSession(),
        )
