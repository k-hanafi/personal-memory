import os
import re
from pathlib import Path

from personal_memory.check import check_brain

ROOT = Path(__file__).resolve().parents[1]
BRAIN = ROOT / "evals" / "brain"
DEFAULT_DENY = ROOT / "evals" / "deny-list.txt"


def test_eval_brain_has_no_denied_names() -> None:
    deny_path = Path(os.environ.get("PERSONAL_MEMORY_DENY_LIST", DEFAULT_DENY))
    entries = []
    for line in deny_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        entries.append(stripped.lower())

    hits: list[str] = []
    for path in sorted(p for p in BRAIN.rglob("*") if p.is_file()):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for entry in entries:
                if re.search(rf"\b{re.escape(entry)}\b", line, re.IGNORECASE):
                    rel = path.relative_to(ROOT)
                    hits.append(f"{rel}:{number}: {entry}")
    assert not hits, "denied names in evals/brain:\n" + "\n".join(hits)


def test_eval_brain_passes_check() -> None:
    result = check_brain(BRAIN)
    assert result.ok, [f"{i.path.name}: {i.message}" for i in result.issues]
