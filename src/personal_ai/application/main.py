from personal_ai.application.bootstrap import bootstrap


def main() -> int:
    bootstrap()
    print("Personal AI initialized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
