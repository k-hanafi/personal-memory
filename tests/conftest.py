import pytest

from personal_memory.cli import main


@pytest.fixture
def _cli():
    def run(argv: list[str]) -> int:
        try:
            return main(argv)
        except SystemExit as exc:
            return int(exc.code or 0)

    return run
