from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from mcp.server import MCPServer

from personal_memory.filing import Proposal, apply, list_queue, remember, submit
from personal_memory.get import get_note
from personal_memory.recall import recall
from personal_memory.unfiled import unfiled

TOOL_NAMES = (
    "remember",
    "revisit",
    "inbox",
    "draft",
    "pending",
    "file",
    "note",
)


def handle(name: str, brain: Path, arguments: dict) -> dict:
    root = brain.expanduser().resolve()
    sources = arguments.get("sources", "sources")
    if name == "remember":
        result = recall(root, arguments["query"], historical=bool(arguments.get("historical")))
        return {"cards": [_card(card) for card in result.cards]}
    if name == "revisit":
        doc = get_note(root, arguments["key"])
        if doc is None:
            return {"text": None, "path": None}
        return {"text": doc.text, "path": doc.path.as_posix()}
    if name == "inbox":
        result = unfiled(root, sources_dir=sources)
        return {"sources": result.sources, "unfiled": [path.as_posix() for path in result.unfiled]}
    if name == "draft":
        proposal = Proposal.from_dict(arguments["proposal"])
        return asdict(submit(root, proposal, sources_dir=sources))
    if name == "pending":
        items = list_queue(root, sources_dir=sources)
        return {
            "items": [
                {
                    "id": item.proposal_id,
                    "submitted_at": item.submitted_at,
                    "proposal": asdict(item.proposal),
                    "outcome": asdict(item.outcome),
                }
                for item in items
            ]
        }
    if name == "file":
        outcomes = apply(root, proposal_id=arguments.get("id"), sources_dir=sources)
        return {"outcomes": [asdict(outcome) for outcome in outcomes]}
    if name == "note":
        provenance = arguments.get("provenance")
        if not provenance or not str(provenance).strip():
            raise ValueError("provenance is required")
        claim = arguments.get("claim")
        if not claim:
            raise ValueError("claim is required")
        return asdict(
            remember(
                root,
                claim,
                str(provenance),
                target=arguments.get("target"),
                path=arguments.get("path"),
                type=arguments.get("type"),
                as_of=arguments.get("as_of"),
                title=arguments.get("title"),
                sources_dir=sources,
            )
        )
    raise ValueError(f"unknown tool: {name}")


def serve(brain: Path) -> None:
    server = MCPServer("personal-memory")

    @server.tool()
    def remember(query: str, historical: bool = False) -> dict:
        """Search the brain. Returns evidence cards with path, lines, status, as_of, and confidence."""
        return handle("remember", brain, {"query": query, "historical": historical})

    @server.tool()
    def revisit(key: str) -> dict:
        """Open one note by id or path. Frontmatter stays intact."""
        return handle("revisit", brain, {"key": key})

    @server.tool()
    def inbox() -> dict:
        """List leftover files under sources/ that no note has filed yet."""
        return handle("inbox", brain, {})

    @server.tool()
    def draft(proposal: dict) -> dict:
        """Queue a filing draft after checking the rules. Writes no note."""
        return handle("draft", brain, {"proposal": proposal})

    @server.tool()
    def pending() -> dict:
        """List filing drafts waiting for review."""
        return handle("pending", brain, {})

    @server.tool()
    def file(id: str | None = None) -> dict:
        """Write queued drafts that pass the rules. Pass id to write one at any confidence."""
        return handle("file", brain, {"id": id})

    @server.tool()
    def note(
        claim: str,
        provenance: str,
        target: str | None = None,
        path: str | None = None,
        type: str | None = None,
        as_of: str | None = None,
        title: str | None = None,
    ) -> dict:
        """Write one fact said in chat. Provenance is required."""
        return handle(
            "note",
            brain,
            {
                "claim": claim,
                "provenance": provenance,
                "target": target,
                "path": path,
                "type": type,
                "as_of": as_of,
                "title": title,
            },
        )

    server.run()


def _card(card) -> dict:
    return {
        "claim": card.claim,
        "path": card.path.as_posix(),
        "start_line": card.start_line,
        "end_line": card.end_line,
        "status": card.status,
        "as_of": card.as_of,
        "confidence": card.confidence,
        "contradicted_by": list(card.contradicted_by),
    }
