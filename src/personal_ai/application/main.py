import argparse

from personal_ai.application.bootstrap import bootstrap

__version__ = "0.2.0"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="personal-ai",
        description="Personal AI Agent System",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.parse_args(argv)

    bootstrap()
    print("Personal AI initialized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
