"""Pydantic models for orchestrator artifacts."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field


class MailThread(BaseModel):
    """Structured representation of a mail thread."""

    path: Path
    project: str
    agent: str | None = None
    body: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "arbitrary_types_allowed": True,
    }

    @classmethod
    def from_path(cls, path: Path) -> "MailThread":
        body = path.read_text(encoding="utf-8")
        parts = path.stem.split("__")
        project = parts[0] if parts else "unknown"
        agent = parts[1] if len(parts) > 1 else None
        stat = path.stat()
        updated_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        return cls(path=path, project=project, agent=agent, body=body, updated_at=updated_at)

    def summary(self, max_lines: int = 4) -> str:
        """Return a trimmed preview of the thread body."""

        lines = [line.rstrip() for line in self.body.splitlines() if line.strip()]
        preview = lines[:max_lines]
        if len(lines) > max_lines:
            preview.append("…")
        return "\n".join(preview)

    def reply_filename(self, suffix: str = "response") -> str:
        """Generate a reply filename that mirrors the inbound thread."""

        base = self.path.stem
        return f"{base}__{suffix}.md"
