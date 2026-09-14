from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from mcp.server import MCPServer

from personal_memory.filing import Proposal, apply, list_queue, note as write_note, submit
from personal_memory.get import get_note
from personal_memory.recall import recall
from personal_memory.unfiled import unfiled


def make_server(brain: Path, sources: str = "sources") -> MCPServer:
    root = brain.expanduser().resolve()
    server = MCPServer("personal-memory")

    @server.tool()
    def remember(query: str, historical: bool = False) -> dict:
        """Search the brain. Returns evidence cards with path, lines, status, as_of, and confidence."""
        result = recall(root, query, historical=historical)
        return {"cards": [_card(card) for card in result.cards]}

    @server.tool()
    def revisit(key: str) -> dict:
        """Open one note by id or path. Frontmatter stays intact."""
        doc = get_note(root, key)
        if doc is None:
            return {"text": None, "path": None}
        return {"text": doc.text, "path": doc.path.as_posix()}

    @server.tool()
    def inbox() -> dict:
        """List leftover files under the dump folder that no note has filed yet."""
        result = unfiled(root, sources_dir=sources)
        return {"sources": result.sources, "unfiled": [path.as_posix() for path in result.unfiled]}

    @server.tool()
    def draft(
        kind: str = "",
        provenance: str = "",
        confidence: str = "",
        as_of: str = "",
        path: str | None = None,
        id: str | None = None,
        type: str | None = None,
        title: str | None = None,
        body: str = "",
        aliases: str | None = None,
        source: str | None = None,
        supersedes: str | None = None,
        target: str | None = None,
        claim: str | None = None,
    ) -> dict:
        """Queue a filing draft after checking the rules. Writes no note."""
        return asdict(
            submit(
                root,
                Proposal(
                    kind,
                    provenance,
                    confidence,
                    as_of,
                    path=path,
                    id=id,
                    type=type,
                    title=title,
                    body=body,
                    aliases=aliases,
                    source=source,
                    supersedes=supersedes,
                    target=target,
                    claim=claim,
                ),
                sources_dir=sources,
            )
        )

    @server.tool()
    def pending() -> dict:
        """List filing drafts waiting for review."""
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

    @server.tool()
    def file(id: str | None = None) -> dict:
        """Write queued drafts that pass the rules. Pass id to write one at any confidence."""
        outcomes = apply(root, proposal_id=id, sources_dir=sources)
        return {"outcomes": [asdict(outcome) for outcome in outcomes]}

    @server.tool()
    def note(
        claim: str = "",
        provenance: str = "",
        target: str | None = None,
        path: str | None = None,
        type: str | None = None,
        as_of: str | None = None,
    ) -> dict:
        """Write one fact said in chat. Empty claim or provenance is a blocked Outcome."""
        return asdict(
            write_note(
                root,
                claim,
                provenance,
                target=target,
                path=path,
                type=type,
                as_of=as_of,
                sources_dir=sources,
            )
        )

    return server


def serve(brain: Path, sources: str = "sources") -> None:
    make_server(brain, sources).run()


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
