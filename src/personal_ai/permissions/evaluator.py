from personal_ai.permissions.policy import PermissionPolicy


class PermissionEvaluator:
    def __init__(self, policy: PermissionPolicy) -> None:
        self.policy = policy

    def evaluate(
        self,
        resource_category: str,
        operation: str,
    ) -> str:
        if not isinstance(resource_category, str):
            raise ValueError("resource_category must be a string")

        if not isinstance(operation, str):
            raise ValueError("operation must be a string")

        defaults = self.policy.get_defaults()

        resource_permissions = defaults.get(resource_category)

        if not isinstance(resource_permissions, dict):
            return "denied"

        if operation in self.policy.get_confirmation_required():
            return "confirmation_required"

        if resource_permissions.get(operation) is True:
            return "allowed"

        return "denied"
