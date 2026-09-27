from __future__ import annotations

import os
from dataclasses import dataclass

from personal_ai.application.config import ApplicationConfig
from personal_ai.application.local_retriever import create_local_retriever
from personal_ai.application.paths import ApplicationPaths
from personal_ai.core.agent import Agent
from personal_ai.core.agent_router import AgentRoute, AgentRouter
from personal_ai.core.automation_scheduler import AutomationScheduler
from personal_ai.core.conversation_session import ConversationSession
from personal_ai.core.executor import Executor
from personal_ai.core.llm_factory import create_llm_provider
from personal_ai.core.llm_integration import LLMIntegration
from personal_ai.core.llm_runtime import LLMRuntime
from personal_ai.core.planner import DeterministicPlanner
from personal_ai.permissions.evaluator import PermissionEvaluator


@dataclass(frozen=True)
class ApplicationRuntime:
    paths: ApplicationPaths
    config: ApplicationConfig
    permission_evaluator: PermissionEvaluator
    planner: DeterministicPlanner
    executor: Executor
    agent: Agent
    agent_router: AgentRouter
    automation_scheduler: AutomationScheduler


def bootstrap(paths: ApplicationPaths | None = None) -> ApplicationRuntime:
    resolved_paths = paths or ApplicationPaths.from_environment()
    config = ApplicationConfig.from_paths(resolved_paths)

    provider_id = os.environ.get("PERSONAL_AI_LLM_PROVIDER", "fake")
    provider = create_llm_provider(config.llm_config, provider_id)

    runtime = LLMRuntime(provider)
    integration = LLMIntegration(runtime)
    permission_evaluator = PermissionEvaluator(config.permission_policy)

    retriever = create_local_retriever(
        filesystem_scope=config.filesystem_scope,
        source_config=config.source_config,
        permission_evaluator=permission_evaluator,
    )

    planner = DeterministicPlanner()
    executor = Executor({})

    agent = Agent(
        integration,
        retriever=retriever,
        planner=planner,
        executor=executor,
    )

    agent_router = AgentRouter(
        [
            AgentRoute(
                route_id="general",
                agent=agent,
            ),
        ]
    )

    def automation_dispatcher(route_id: str, request: str) -> object:
        session = ConversationSession(
            session_id=f"automation:{route_id}",
        )
        return agent_router.run(
            route_id=route_id,
            user_request=request,
            session=session,
        )

    automation_scheduler = AutomationScheduler(
        automation_dispatcher,
    )

    return ApplicationRuntime(
        paths=resolved_paths,
        config=config,
        permission_evaluator=permission_evaluator,
        planner=planner,
        executor=executor,
        agent=agent,
        agent_router=agent_router,
        automation_scheduler=automation_scheduler,
    )
