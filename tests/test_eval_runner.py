from pathlib import Path
import json

from personal_memory.cli import main
from personal_memory.evals.receipt import write_receipt
from personal_memory.evals.report import render
from personal_memory.evals.runner import fixtures_hash, run

ROOT = Path(__file__).resolve().parents[1]

SMOKE = """
family = "smoke"

[[case]]
id = "top"
query = "budget"
expect_path = "b.md"
expect_status = "current"

[[case]]
id = "by-id"
query = "b"
expect_path = "b.md"
holdout = true

[[case]]
id = "absent"
query = "quantum pineapple syllabus"
abstain = true
"""

NOTE = """---
id: {id}
type: area
as_of: 2026-09-01
status: {status}
confidence: high
---

# {id}

{body}
"""


def _strip_timestamp(receipt: dict) -> dict:
    return {key: value for key, value in receipt.items() if key != "timestamp"}


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def _budget_corpus(tmp_path: Path) -> Path:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    _write(corpus / "b.md", NOTE.format(id="b", status="current", body="budget budget budget"))
    _write(corpus / "a.md", NOTE.format(id="a", status="superseded", body="budget once"))
    _write(corpus / "c.md", NOTE.format(id="c", status="current", body="budget once"))
    _write(corpus / "d.md", NOTE.format(id="d", status="current", body="nothing relevant"))
    return corpus


def test_receipt_shape_and_determinism(tmp_path: Path) -> None:
    corpus = _budget_corpus(tmp_path)
    fixture = _write(tmp_path / "smoke.toml", SMOKE)
    first = run(corpus, fixture, ["recall", "grep"])
    second = run(corpus, fixture, ["recall", "grep"])
    assert _strip_timestamp(first) == _strip_timestamp(second)
    assert "timestamp" not in _strip_timestamp(first)
    assert "timestamp" in first

    write_receipt(first, tmp_path / "runs" / "a.json")
    write_receipt(second, tmp_path / "runs" / "b.json")
    a = json.loads((tmp_path / "runs" / "a.json").read_text())
    b = json.loads((tmp_path / "runs" / "b.json").read_text())
    assert _strip_timestamp(a) == _strip_timestamp(b)
    assert (tmp_path / "runs" / "a.json").read_text().endswith("}\n")

    assert set(first) == {"commit", "fixtures_hash", "corpus", "fixtures", "timestamp", "adapters"}
    assert first["fixtures_hash"] == fixtures_hash(fixture, corpus)
    assert set(first["adapters"]) == {"recall", "grep"}
    for result in first["adapters"].values():
        assert set(result) == {"families", "superseded_leaks", "abstention_accuracy"}
        family = result["families"]["smoke"]
        assert set(family) == {"passed", "total", "hit_at_1", "recall_at_5", "cases"}
        assert family["total"] == 3
        assert family["passed"] == sum(case["pass"] for case in family["cases"].values())
        for case in family["cases"].values():
            assert set(case) == {"pass", "failure", "holdout", "hits"}
            assert case["pass"] == (case["failure"] is None)
            assert len(case["hits"]) <= 5
            for hit in case["hits"]:
                assert set(hit) == {"path", "start_line", "end_line", "status", "confidence", "contradicted_by"}
        assert family["cases"]["by-id"]["holdout"] is True

    recall_smoke = first["adapters"]["recall"]["families"]["smoke"]
    assert recall_smoke["passed"] == 3
    assert recall_smoke["cases"]["top"]["hits"][0]["path"] == "b.md"


def test_hit_at_1_recall_at_5_and_abstention_on_known_corpus(tmp_path: Path) -> None:
    corpus = _budget_corpus(tmp_path)
    fixture = _write(
        tmp_path / "budget.toml",
        """
family = "budget"

[[case]]
id = "top"
query = "budget"
expect_path = "b.md"

[[case]]
id = "third"
query = "budget"
expect_path = "c.md"

[[case]]
id = "absent"
query = "budget"
expect_path = "d.md"

[[case]]
id = "abstain-ok"
query = "zzz"
abstain = true

[[case]]
id = "abstain-bad"
query = "budget"
abstain = true
""",
    )
    receipt = run(corpus, fixture, ["recall", "grep"])
    grep = receipt["adapters"]["grep"]
    family = grep["families"]["budget"]
    assert family["passed"] == 2
    assert family["total"] == 5
    assert family["hit_at_1"] == 0.3333
    assert family["recall_at_5"] == 0.6667
    assert family["cases"]["third"]["failure"] == "expect_path"
    assert family["cases"]["abstain-bad"]["failure"] == "abstain"
    assert grep["abstention_accuracy"] == 0.5
    # b (current), a (superseded), c (current): a outranks c on every non-abstaining "budget" query.
    assert grep["superseded_leaks"] == 4
    assert receipt["adapters"]["recall"]["superseded_leaks"] == 0


def test_abstention_accuracy_is_null_without_abstain_cases(tmp_path: Path) -> None:
    fixture = _write(
        tmp_path / "one.toml",
        """
family = "one"

[[case]]
id = "top"
query = "budget"
expect_path = "b.md"
""",
    )
    receipt = run(_budget_corpus(tmp_path), fixture, ["grep"])
    assert receipt["adapters"]["grep"]["abstention_accuracy"] is None


def test_family_filter_and_single_file_versus_directory(tmp_path: Path) -> None:
    corpus = _budget_corpus(tmp_path)
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    _write(fixtures / "smoke.toml", SMOKE)
    _write(
        fixtures / "other.toml",
        """
family = "other"

[[case]]
id = "also"
query = "budget"
expect_path = "b.md"
""",
    )
    both = run(corpus, fixtures, ["grep"])
    assert list(both["adapters"]["grep"]["families"]) == ["other", "smoke"]
    only = run(corpus, fixtures, ["grep"], families=["smoke"])
    assert list(only["adapters"]["grep"]["families"]) == ["smoke"]
    single = run(corpus, fixtures / "smoke.toml", ["grep"])
    assert single["adapters"]["grep"]["families"]["smoke"] == both["adapters"]["grep"]["families"]["smoke"]


def test_fixtures_hash_tracks_fixture_and_corpus_bytes(tmp_path: Path) -> None:
    corpus = _budget_corpus(tmp_path)
    fixture = _write(tmp_path / "one.toml", 'family = "one"\n')
    before = fixtures_hash(fixture, corpus)
    assert before == fixtures_hash(fixture, corpus)
    _write(corpus / "d.md", NOTE.format(id="d", status="current", body="changed"))
    after_corpus = fixtures_hash(fixture, corpus)
    assert after_corpus != before
    _write(fixture, 'family = "two"\n')
    assert fixtures_hash(fixture, corpus) != after_corpus


def test_render_table() -> None:
    receipt = {
        "adapters": {
            "recall": {
                "families": {
                    "smoke": {"passed": 3, "total": 3},
                    "extra": {"passed": 1, "total": 12},
                }
            },
            "grep": {
                "families": {
                    "smoke": {"passed": 1, "total": 3},
                    "extra": {"passed": 0, "total": 12},
                }
            },
        }
    }
    lines = render(receipt).splitlines()
    assert len(lines) == 3
    assert lines[0].split() == ["family", "recall", "grep", "vs", "main"]
    assert lines[1].split() == ["smoke", "3/3", "1/3"]
    assert lines[2].split() == ["extra", "1/12", "0/12"]
    assert lines[0].index("recall") == lines[1].index("3/3") == lines[2].index("1/12")
    assert lines[0].index("grep") == lines[1].index("1/3") == lines[2].index("0/12")


def test_cli_eval_run_writes_receipt(tmp_path: Path, capsys) -> None:
    corpus = _budget_corpus(tmp_path)
    fixture = _write(tmp_path / "smoke.toml", SMOKE)
    out = tmp_path / "runs" / "r.json"
    code = main(
        ["eval", "run", "--fixtures", str(fixture), "--corpus", str(corpus), "--adapter", "grep", "--out", str(out)]
    )
    assert code == 0
    printed = capsys.readouterr().out.splitlines()
    assert printed[0].split() == ["family", "grep", "vs", "main"]
    assert printed[-1] == str(out)
    receipt = json.loads(out.read_text(encoding="utf-8"))
    assert list(receipt["adapters"]) == ["grep"]
    assert receipt["adapters"]["grep"]["families"]["smoke"]["total"] == 3


def test_cli_eval_gate_missing_corpus_exits_2(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "no-brain"
    code = main(
        [
            "eval",
            "gate",
            "--main-baseline",
            str(tmp_path / "baseline.json"),
            "--corpus",
            str(missing),
            "--fixtures",
            str(ROOT / "evals" / "fixtures"),
        ]
    )
    captured = capsys.readouterr()
    assert code == 2
    assert "not a directory" in captured.err
    assert "gate:" not in captured.out


def test_cli_eval_run_missing_fixtures_exits_2(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "nope"
    code = main(["eval", "run", "--fixtures", str(missing), "--corpus", str(tmp_path), "--out", str(tmp_path / "r.json")])
    assert code == 2
    assert "does not exist" in capsys.readouterr().err
    assert not (tmp_path / "r.json").exists()


def test_cli_eval_run_empty_fixtures_dir_exits_2(tmp_path: Path, capsys) -> None:
    empty = tmp_path / "fixtures"
    empty.mkdir()
    code = main(["eval", "run", "--fixtures", str(empty), "--corpus", str(tmp_path), "--out", str(tmp_path / "r.json")])
    assert code == 2
    assert "no fixture families" in capsys.readouterr().err
