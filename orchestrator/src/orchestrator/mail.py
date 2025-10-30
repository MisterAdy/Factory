"""Mail bus helpers for reading and writing Git-backed threads."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Iterator

from .models import MailThread


class Mailbox:
    """Simple mailbox abstraction for inbox/outbox directories."""

    def __init__(
        self,
        inbox: Path | str,
        *,
        outbox: Path | str | None = None,
        glob_mode: bool = False,
    ) -> None:
        self.inbox = Path(inbox)
        self.outbox = Path(outbox) if outbox is not None else None
        self.glob_mode = glob_mode
        self._seen: Dict[Path, float] = {}

    def inbox_threads(self) -> Iterator[MailThread]:
        """Iterate over newly updated inbound threads."""

        if self.glob_mode:
            base = self.inbox.parent
            matches: Iterable[Path] = base.glob(self.inbox.name)
        else:
            matches = self.inbox.glob("*")
        for path in sorted(matches):
            if not path.is_file():
                continue
            modified = path.stat().st_mtime
            if self._seen.get(path) == modified:
                continue
            self._seen[path] = modified
            yield MailThread.from_path(path)

    def ensure_outbox(self) -> Path:
        """Ensure the outbox directory exists."""

        if self.outbox is None:
            raise ValueError("Outbox directory not configured for this mailbox")
        self.outbox.mkdir(parents=True, exist_ok=True)
        return self.outbox

    def write_reply(self, name: str, body: str) -> Path:
        """Write a reply into the outbox directory."""

        outbox = self.ensure_outbox()
        target = outbox / name
        target.write_text(body, encoding="utf-8")
        return target
