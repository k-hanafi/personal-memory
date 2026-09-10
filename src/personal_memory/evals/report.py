from __future__ import annotations

from personal_memory.evals.baseline import GATED_ADAPTER, compare


def render(receipt: dict, main_baseline: dict | None = None) -> str:
    """One row per family, one column per adapter with passed/total, and a vs main column of recall flips."""
    adapters = receipt["adapters"]
    family_names = next((list(result["families"]) for result in adapters.values()), [])
    comparison = None
    if main_baseline is not None and GATED_ADAPTER in adapters:
        comparison = compare(main_baseline, receipt)
    rows = [["family", *adapters, "vs main"]]
    for name in family_names:
        counts = [result["families"][name] for result in adapters.values()]
        vs_main = ""
        if comparison is not None:
            improved = comparison.improved.get(GATED_ADAPTER, {}).get(name, [])
            regressed = comparison.regressed.get(GATED_ADAPTER, {}).get(name, [])
            vs_main = f"+{len(improved)} / -{len(regressed)}"
            if regressed:
                vs_main += f"  <- FAIL: {', '.join(regressed)}"
        rows.append([name, *(f"{c['passed']}/{c['total']}" for c in counts), vs_main])
    widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
    return "\n".join("  ".join(cell.ljust(width) for cell, width in zip(row, widths)).rstrip() for row in rows)
