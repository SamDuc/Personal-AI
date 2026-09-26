from abc import ABC, abstractmethod

from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.tools.model import ToolResult


class Tool(ABC):
    @abstractmethod
    def execute(
        self,
        input_data: object,
        permission_evaluator: PermissionEvaluator,
    ) -> ToolResult:
        """Execute the tool with permission evaluation."""
        raise NotImplementedError
