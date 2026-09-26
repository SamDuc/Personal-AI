from copy import deepcopy
from pathlib import Path

import yaml


class PermissionPolicy:
    def __init__(self, policy: dict) -> None:
        if not isinstance(policy, dict):
            raise ValueError("policy must be a dictionary")

        self.policy = policy

    @classmethod
    def from_file(cls, path: str | Path) -> "PermissionPolicy":
        policy_path = Path(path)

        if not policy_path.is_file():
            raise FileNotFoundError(
                f"permission policy not found: {policy_path}"
            )

        with policy_path.open("r", encoding="utf-8") as file:
            policy = yaml.safe_load(file)

        return cls(policy)

    def get_defaults(self) -> dict:
        defaults = self.policy.get("defaults", {})

        if not isinstance(defaults, dict):
            raise ValueError("permission defaults must be a dictionary")

        return deepcopy(defaults)

    def get_confirmation_required(self) -> list[str]:
        operations = self.policy.get("confirmation_required", [])

        if not isinstance(operations, list):
            raise ValueError(
                "confirmation_required must be a list"
            )

        return list(operations)
