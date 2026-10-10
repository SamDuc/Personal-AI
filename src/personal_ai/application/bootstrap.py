from __future__ import annotations

import os
from dataclasses import dataclass

from personal_ai.application.canonical_content_access import (
    LocalCanonicalContentAccess,
)
from personal_ai.application.canonical_retriever import LocalCanonicalRetrieval
from personal_ai.application.config import ApplicationConfig
from personal_ai.application.paths import ApplicationPaths
from personal_ai.core.agent import Agent
from personal_ai.core.agent_router import AgentRoute, AgentRouter
from personal_ai.core.automation_scheduler import AutomationScheduler
from personal_ai.core.conversation_session import ConversationSession
from personal_ai.core.executor import Executor
from personal_ai.core.llm_execution_strategy import ExecutionStrategyResolver
from personal_ai.core.llm_integration import LLMIntegration
from personal_ai.core.llm_provider_registry import ProviderRegistry
from personal_ai.core.llm_provider_resolver import ProviderResolver
from personal_ai.core.llm_runtime import LLMRuntime
from personal_ai.core.planner import DeterministicPlanner
from personal_ai.file_intelligence.index import ContentIndex
from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.tools.executor import ToolExecutor
from personal_ai.tools.registry import ToolRegistry


@dataclass(frozen=True)
class ApplicationRuntime:
    paths: ApplicationPaths
    config: ApplicationConfig
    permission_evaluator: PermissionEvaluator
    tool_registry: ToolRegistry
    tool_executor: ToolExecutor
    planner: DeterministicPlanner
    executor: Executor
    agent: Agent
    retrieval: LocalCanonicalRetrieval
    agent_router: AgentRouter
    automation_scheduler: AutomationScheduler


def bootstrap(paths: ApplicationPaths | None = None) -> ApplicationRuntime:
    resolved_paths = paths or ApplicationPaths.from_environment()
    config = ApplicationConfig.from_paths(resolved_paths)

    provider_id = os.environ.get("PERSONAL_AI_LLM_PROVIDER", "fake")
    provider_registry = ProviderRegistry(config.llm_config)
    provider_resolver = ProviderResolver(provider_registry)

    execution_strategy_resolver = ExecutionStrategyResolver(provider_resolver)
    execution_strategy_resolver.resolve(provider_id)
    provider = provider_resolver.resolve(provider_id).provider

    runtime = LLMRuntime(provider)
    integration = LLMIntegration(runtime)
    permission_evaluator = PermissionEvaluator(config.permission_policy)

    content_index = ContentIndex()
    retrieval = LocalCanonicalRetrieval(
        filesystem_scope=config.filesystem_scope,
        source_config=config.source_config,
        permission_evaluator=permission_evaluator,
        content_index=content_index,
    )
    content_access = LocalCanonicalContentAccess(
        filesystem_scope=config.filesystem_scope,
        source_config=config.source_config,
        permission_evaluator=permission_evaluator,
        content_index=content_index,
    )

    planner = DeterministicPlanner()
    executor = Executor({})

    tool_registry = ToolRegistry()
    tool_executor = ToolExecutor()

    agent = Agent(
        integration,
        retrieval=retrieval,
        content_access=content_access,
        planner=planner,
        executor=executor,
        tool_registry=tool_registry,
        tool_executor=tool_executor,
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
        tool_registry=tool_registry,
        tool_executor=tool_executor,
        planner=planner,
        executor=executor,
        agent=agent,
        retrieval=retrieval,
        agent_router=agent_router,
        automation_scheduler=automation_scheduler,
    )
