from pathlib import Path
import copy
import json

import pytest

from personal_memory.cli import main
from personal_memory.evals.baseline import compare, gate, gold, to_baseline
from personal_memory.evals.receipt import write_receipt
from personal_memory.evals.report import render
from personal_memory.evals.runner import run

ROOT = Path(__file__).resolve().parents[1]
BRAIN = ROOT / "evals" / "brain"
FIXTURES = ROOT / "evals" / "fixtures"
COMMITTED = ROOT / "evals" / "baselines" / "main.json"


def _case(passed: bool, holdout: bool = False) -> dict:
    return {"pass": passed, "failure": None if passed else "expect_path", "holdout": holdout, "hits": [{"path": "x"}]}


def _receipt(recall: dict[str, dict[str, bool]], grep: dict[str, dict[str, bool]] | None = None, hash_: str = "h1") -> dict:
    """Small receipt from {family: {case_id: pass}} maps. A case id ending in '!' is holdout."""
    if grep is None:
        grep = {name: {cid: False for cid in cases} for name, cases in recall.items()}

    def adapter(families: dict[str, dict[str, bool]]) -> dict:
        return {
            "abstention_accuracy": 0.5,
            "superseded_leaks": 0,
            "families": {
                name: {
                    "passed": sum(cases.values()),
                    "total": len(cases),
                    "hit_at_1": 0.5,
                    "recall_at_5": 0.5,
                    "cases": {cid.rstrip("!"): _case(ok, holdout=cid.endswith("!")) for cid, ok in cases.items()},
                }
                for name, cases in families.items()
            },
        }

    return {
        "commit": "abc",
        "timestamp": "2026-09-09T00:00:00+00:00",
        "fixtures_hash": hash_,
        "corpus": "evals/brain",
        "fixtures": "evals/fixtures",
        "adapters": {"recall": adapter(recall), "grep": adapter(grep)},
    }


MAIN = _receipt({"named": {"a": True, "b": False, "c": True, "h!": True}}, {"named": {"a": False}})


def test_to_baseline_strips_exactly_timestamp_commit_and_hits() -> None:
    receipt = _receipt({"named": {"a": True}})
    baseline = to_baseline(receipt)
    assert set(baseline) == set(receipt) - {"timestamp", "commit"}
    case = baseline["adapters"]["recall"]["families"]["named"]["cases"]["a"]
    assert set(case) == {"pass", "failure", "holdout"}
    family = baseline["adapters"]["recall"]["families"]["named"]
    assert {k: v for k, v in family.items() if k != "cases"} == {"passed": 1, "total": 1, "hit_at_1": 0.5, "recall_at_5": 0.5}
    assert baseline["adapters"]["recall"]["abstention_accuracy"] == 0.5
    assert baseline["fixtures_hash"] == "h1"
    assert "hits" in receipt["adapters"]["recall"]["families"]["named"]["cases"]["a"]


def test_gold_excludes_failures_and_holdout() -> None:
    assert gold(MAIN, "recall") == {"a", "c"}
    assert gold(MAIN, "grep") == set()


def test_compare_finds_flips_and_respects_holdout() -> None:
    head = _receipt({"named": {"a": False, "b": True, "c": True, "h!": False}}, {"named": {"a": True}}, hash_="h2")
    comparison = compare(MAIN, head)
    assert comparison.improved == {"recall": {"named": ["b"]}, "grep": {"named": ["a"]}}
    assert comparison.regressed == {"recall": {"named": ["a"]}}
    assert comparison.hash_changed is True
    assert compare(MAIN, MAIN).hash_changed is False
    assert compare(MAIN, MAIN).improved == {} and compare(MAIN, MAIN).regressed == {}


def test_gate_rule_a_missing_head_baseline() -> None:
    result = gate(MAIN, to_baseline(MAIN), None)
    assert not result.ok
    assert "no committed baseline" in result.messages[0]
    assert gate(MAIN, to_baseline(MAIN), to_baseline(MAIN)).ok


def test_gate_rule_b_head_must_match_fresh_when_it_differs_from_main() -> None:
    fresh = _receipt({"named": {"a": True, "b": True}})
    head = to_baseline(fresh)
    head["justification"] = "ignored by the byte match"
    assert gate(fresh, None, head).ok
    stale = to_baseline(fresh)
    stale["adapters"]["recall"]["families"]["named"]["passed"] = 1
    result = gate(fresh, None, stale)
    assert not result.ok
    assert result.messages == ["committed baseline does not match a fresh run"]
    # When head equals main, fresh may drift from head without tripping rule b (rule d catches it).
    assert "does not match" not in " ".join(gate(fresh, to_baseline(MAIN), to_baseline(MAIN)).messages)


def test_gate_rule_c_no_main_baseline_passes_with_message() -> None:
    result = gate(MAIN, None, to_baseline(MAIN))
    assert result.ok
    assert "regression check skipped" in result.messages[0]
    assert not gate(MAIN, None, to_baseline(_receipt({"named": {"a": False}}))).ok


def test_gate_rule_d_regression_under_unchanged_hash_fails() -> None:
    fresh = _receipt({"named": {"a": False, "b": False, "c": True, "h!": False}})
    result = gate(fresh, to_baseline(MAIN), to_baseline(MAIN))
    assert not result.ok
    assert "regressed: named/a (recall)" in result.messages
    assert not any("h (recall)" in m for m in result.messages)
    clean = gate(MAIN, to_baseline(MAIN), to_baseline(MAIN))
    assert clean.ok and clean.messages == ["no flips against main"]


def test_gate_rule_d_regression_under_changed_hash_needs_justification() -> None:
    fresh = _receipt({"named": {"a": False, "b": False, "c": True, "h!": True}}, hash_="h2")
    unjustified = to_baseline(fresh)
    result = gate(fresh, to_baseline(MAIN), unjustified)
    assert not result.ok
    assert "regressed: named/a (recall)" in result.messages
    assert "add a justification string to evals/baselines/main.json" in result.messages
    justified = dict(unjustified, justification="a now needs wikilink hops")
    result = gate(fresh, to_baseline(MAIN), justified)
    assert result.ok
    assert "justification: a now needs wikilink hops" in result.messages
    assert not gate(fresh, to_baseline(MAIN), dict(unjustified, justification="   ")).ok


def test_gate_rule_e_gold_count_may_not_fall_without_justification() -> None:
    # Case c removed from the fixtures: no regression, but fewer gold cases.
    fresh = _receipt({"named": {"a": True, "b": False, "h!": True}}, hash_="h2")
    result = gate(fresh, to_baseline(MAIN), to_baseline(fresh))
    assert not result.ok
    assert "gold count fell from 2 to 1" in result.messages
    assert gate(fresh, to_baseline(MAIN), dict(to_baseline(fresh), justification="dropped c")).ok
    grew = _receipt({"named": {"a": True, "b": True, "c": True, "h!": True}}, hash_="h2")
    assert gate(grew, to_baseline(MAIN), to_baseline(grew)).ok


def test_gate_rule_f_improvements_are_info_and_prompt_promotion() -> None:
    fresh = _receipt({"named": {"a": True, "b": True, "c": True, "h!": True}})
    result = gate(fresh, to_baseline(MAIN), to_baseline(MAIN))
    assert result.ok
    assert "improved: named/b (recall)" in result.messages
    assert "run eval run --update-baseline to promote them" in result.messages
    promoted = gate(fresh, to_baseline(MAIN), to_baseline(fresh))
    assert promoted.ok
    assert "improved: named/b (recall)" in promoted.messages
    assert not any("promote" in m for m in promoted.messages)


def test_grep_never_gates() -> None:
    main = _receipt({"named": {"a": True}}, {"named": {"g": True}})
    fresh = _receipt({"named": {"a": True}}, {"named": {"g": False}})
    result = gate(fresh, to_baseline(main), to_baseline(main))
    assert result.ok
    assert not any("grep" in m for m in result.messages)


def test_render_vs_main_column() -> None:
    fresh = _receipt({"named": {"a": False, "b": True, "c": True, "h!": True}, "other": {"x": True}})
    lines = render(fresh, to_baseline(MAIN)).splitlines()
    assert lines[1].endswith("+1 / -1  <- FAIL: a")
    assert lines[2].endswith("+0 / -0")
    assert render(fresh).splitlines()[1].split() == ["named", "3/4", "0/4"]


def test_cli_compare_prints_flips(tmp_path: Path, capsys) -> None:
    head = _receipt({"named": {"a": False, "b": True, "c": True, "h!": True}}, hash_="h2")
    write_receipt(MAIN, tmp_path / "main.json")
    write_receipt(to_baseline(head), tmp_path / "head.json")
    assert main(["eval", "compare", str(tmp_path / "main.json"), str(tmp_path / "head.json")]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0] == "grep"
    assert out[1].split() == ["named", "+0", "/", "-0"]
    start = out.index("recall")
    assert out[start + 1].split() == ["named", "+1", "/", "-1"]
    assert out[start + 2].strip() == "+ b"
    assert out[start + 3].strip() == "- a"
    assert out[-1] == "fixtures hash changed"


def test_cli_update_baseline_preserves_justification_and_rejects_allow_regression(tmp_path: Path, capsys) -> None:
    baseline = tmp_path / "main.json"
    fixture = FIXTURES / "contradiction.toml"
    base_args = ["eval", "run", "--fixtures", str(fixture), "--corpus", str(BRAIN), "--out", str(tmp_path / "r.json")]
    assert main([*base_args, "--baseline", str(baseline), "--update-baseline"]) == 0
    assert capsys.readouterr().out.splitlines()[-1] == str(baseline)
    written = json.loads(baseline.read_text())
    assert set(written) == {"adapters", "corpus", "fixtures", "fixtures_hash"}
    written["justification"] = "keep me"
    baseline.write_text(json.dumps(written))
    assert main([*base_args, "--baseline", str(baseline), "--update-baseline"]) == 0
    assert json.loads(baseline.read_text())["justification"] == "keep me"
    assert "+0 / -0" in capsys.readouterr().out

    assert main([*base_args, "--allow-regression", "trying things"]) == 0
    assert json.loads((tmp_path / "r.json").read_text())["allow_regression"] == "trying things"
    with pytest.raises(SystemExit):
        main([*base_args, "--update-baseline", "--allow-regression", "no"])


def test_committed_baseline_matches_fresh_run_and_gate_passes(monkeypatch) -> None:
    monkeypatch.chdir(ROOT)
    fresh = run(Path("evals/brain"), Path("evals/fixtures"), ["recall", "grep"])
    committed = json.loads(COMMITTED.read_text(encoding="utf-8"))
    assert to_baseline(fresh) == {k: v for k, v in committed.items() if k != "justification"}
    result = gate(fresh, committed, committed)
    assert result.ok


def test_gate_names_regressed_case_against_real_run(monkeypatch) -> None:
    monkeypatch.chdir(ROOT)
    fresh = run(Path("evals/brain"), Path("evals/fixtures"), ["recall", "grep"])
    committed = json.loads(COMMITTED.read_text(encoding="utf-8"))
    families = fresh["adapters"]["recall"]["families"]
    failing = next(
        (f, c) for f in families for c, v in families[f]["cases"].items() if not v["pass"] and not v["holdout"]
    )
    main_baseline = copy.deepcopy(committed)
    main_baseline["adapters"]["recall"]["families"][failing[0]]["cases"][failing[1]]["pass"] = True
    result = gate(fresh, main_baseline, committed)
    assert not result.ok
    assert f"regressed: {failing[0]}/{failing[1]} (recall)" in result.messages

    tampered = copy.deepcopy(committed)
    tampered["adapters"]["recall"]["superseded_leaks"] += 1
    assert gate(fresh, committed, tampered).messages == ["committed baseline does not match a fresh run"]


def test_cli_gate_exits_0_against_copy_of_committed_baseline(tmp_path: Path, capsys, monkeypatch) -> None:
    monkeypatch.chdir(ROOT)
    copy_path = tmp_path / "main.json"
    copy_path.write_bytes(COMMITTED.read_bytes())
    assert main(["eval", "gate", "--main-baseline", str(copy_path)]) == 0
    out = capsys.readouterr().out
    assert "+0 / -0" in out and "gate: ok" in out
    assert main(["eval", "gate", "--main-baseline", str(tmp_path / "missing.json")]) == 0
    assert "regression check skipped" in capsys.readouterr().out
