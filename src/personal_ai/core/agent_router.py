from dataclasses import dataclass
from typing import Protocol

from personal_ai.core.conversation_session import ConversationSession


class RoutableAgent(Protocol):
    def run(
        self,
        user_request: str,
        session: ConversationSession,
    ) -> str: ...


@dataclass(frozen=True)
class AgentRoute:
    route_id: str
    agent: RoutableAgent


class AgentRouter:
    def __init__(self, routes: list[AgentRoute]) -> None:
        self._routes = {}

        for route in routes:
            if not isinstance(route.route_id, str) or not route.route_id:
                raise ValueError("route_id must be a non-empty string")

            if route.route_id in self._routes:
                raise ValueError(f"duplicate route: {route.route_id}")

            self._routes[route.route_id] = route.agent

    @property
    def route_ids(self) -> tuple[str, ...]:
        return tuple(self._routes)

    def resolve(self, route_id: str) -> RoutableAgent:
        if not isinstance(route_id, str) or not route_id:
            raise ValueError("route_id must be a non-empty string")

        try:
            return self._routes[route_id]
        except KeyError as exc:
            raise ValueError(f"unknown agent route: {route_id}") from exc

    def run(
        self,
        route_id: str,
        user_request: str,
        session: ConversationSession,
    ) -> str:
        if not isinstance(user_request, str):
            raise ValueError("user_request must be a string")

        agent = self.resolve(route_id)

        return agent.run(
            user_request=user_request,
            session=session,
        )
