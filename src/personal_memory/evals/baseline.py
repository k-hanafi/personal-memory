from __future__ import annotations

from dataclasses import dataclass, field

BASELINE_PATH = "evals/baselines/main.json"
GATED_ADAPTER = "recall"

Flips = dict[str, dict[str, list[str]]]


@dataclass
class Comparison:
    improved: Flips = field(default_factory=dict)
    regressed: Flips = field(default_factory=dict)
    hash_changed: bool = False


@dataclass
class GateResult:
    ok: bool
    messages: list[str]


def to_baseline(receipt: dict) -> dict:
    """The receipt without timestamp, commit, or per-case hits, so a diff shows only pass/fail flips."""
    baseline = {key: value for key, value in receipt.items() if key not in ("timestamp", "commit")}
    baseline["adapters"] = {
        name: {
            **result,
            "families": {
                family_name: {
                    **family,
                    "cases": {
                        case_id: {key: value for key, value in case.items() if key != "hits"}
                        for case_id, case in family["cases"].items()
                    },
                }
                for family_name, family in result["families"].items()
            },
        }
        for name, result in receipt["adapters"].items()
    }
    return baseline


def gold(baseline: dict, adapter: str) -> set[str]:
    """Case ids that pass and are not holdout for one adapter."""
    return {
        case_id
        for family in baseline["adapters"].get(adapter, {}).get("families", {}).values()
        for case_id, case in family["cases"].items()
        if case["pass"] and not case["holdout"]
    }


def compare(main: dict, head: dict) -> Comparison:
    """Per adapter and family, which non-holdout cases flipped fail-to-pass or pass-to-fail."""
    comparison = Comparison(hash_changed=main.get("fixtures_hash") != head.get("fixtures_hash"))
    for adapter, head_result in head["adapters"].items():
        main_families = main["adapters"].get(adapter, {}).get("families", {})
        for family_name, head_family in head_result["families"].items():
            main_cases = main_families.get(family_name, {}).get("cases", {})
            improved = []
            regressed = []
            for case_id, head_case in head_family["cases"].items():
                main_case = main_cases.get(case_id)
                if main_case is None or head_case["holdout"] or main_case["holdout"]:
                    continue
                if head_case["pass"] and not main_case["pass"]:
                    improved.append(case_id)
                if main_case["pass"] and not head_case["pass"]:
                    regressed.append(case_id)
            if improved:
                comparison.improved.setdefault(adapter, {})[family_name] = improved
            if regressed:
                comparison.regressed.setdefault(adapter, {})[family_name] = regressed
    return comparison


def gate(fresh: dict, main_baseline: dict | None, head_baseline: dict | None) -> GateResult:
    # Only the recall adapter gates; grep is the baseline row, reported but never gated.
    if head_baseline is None:
        return GateResult(False, [f"no committed baseline at {BASELINE_PATH}; run eval run --update-baseline"])

    if main_baseline is None or head_baseline != main_baseline:
        committed = {key: value for key, value in head_baseline.items() if key != "justification"}
        if committed != to_baseline(fresh):
            return GateResult(False, ["committed baseline does not match a fresh run"])

    if main_baseline is None:
        return GateResult(True, ["no baseline on main to compare against; regression check skipped"])

    head = to_baseline(fresh)
    comparison = compare(main_baseline, head)
    justification = head_baseline.get("justification")
    justified = (
        isinstance(justification, str)
        and justification.strip() != ""
        and justification != main_baseline.get("justification")
    )
    messages: list[str] = []
    ok = True

    regressed = _names(comparison.regressed, GATED_ADAPTER)
    if regressed:
        if comparison.hash_changed and justified:
            messages.append(f"regressed with justification: {', '.join(regressed)}")
            messages.append(f"justification: {justification}")
        else:
            ok = False
            messages.append(f"regressed: {', '.join(regressed)}")
            if comparison.hash_changed:
                messages.append(f"add a justification string to {BASELINE_PATH}")

    main_gold = len(gold(main_baseline, GATED_ADAPTER))
    head_gold = len(gold(head, GATED_ADAPTER))
    if head_gold < main_gold and not justified:
        ok = False
        messages.append(f"gold count fell from {main_gold} to {head_gold}")

    improved = _names(comparison.improved, GATED_ADAPTER)
    if improved:
        messages.append(f"improved: {', '.join(improved)}")
        if head_baseline == main_baseline:
            messages.append("run eval run --update-baseline to promote them")

    if ok and not messages:
        messages.append("no flips against main")
    return GateResult(ok, messages)


def _names(flips: Flips, adapter: str) -> list[str]:
    return [
        f"{family}/{case_id} ({adapter})"
        for family, case_ids in flips.get(adapter, {}).items()
        for case_id in case_ids
    ]
