import sys

from app.modules.orchestrator import EmployeeEvaluationOrchestrator


def main() -> int:
    orchestrator = EmployeeEvaluationOrchestrator()
    return orchestrator.run()


if __name__ == "__main__":
    sys.exit(main())
