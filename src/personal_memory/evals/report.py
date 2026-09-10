from __future__ import annotations


def render(receipt: dict) -> str:
    """One row per family, one column per adapter with passed/total, and a blank vs main column."""
    adapters = receipt["adapters"]
    family_names = next((list(result["families"]) for result in adapters.values()), [])
    rows = [["family", *adapters, "vs main"]]
    for name in family_names:
        counts = [result["families"][name] for result in adapters.values()]
        rows.append([name, *(f"{c['passed']}/{c['total']}" for c in counts), ""])
    widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
    return "\n".join("  ".join(cell.ljust(width) for cell, width in zip(row, widths)).rstrip() for row in rows)
