"""Entry point for the Commerce Factory orchestrator loop."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Iterable

from .config import Settings, load_settings
from .mail import Mailbox
from .models import MailThread


async def handle_thread(mailbox: Mailbox, thread: MailThread) -> None:
    """Placeholder for agent hand-off logic."""

    logger = logging.getLogger(__name__)
    logger.info(
        "Processing thread %s from project=%s agent=%s",
        thread.path.name,
        thread.project,
        thread.agent or "unknown",
    )
    # Simulate async work. Replace with real routing + tool execution.
    await asyncio.sleep(0.05)
    preview = thread.summary()
    logger.debug("Thread preview:\n%s", preview)


async def tick(inboxes: Iterable[Mailbox]) -> None:
    """Process one tick across all monitored inboxes."""

    tasks = []
    for mailbox in inboxes:
        for thread in mailbox.inbox_threads():
            tasks.append(asyncio.create_task(handle_thread(mailbox, thread)))
    if tasks:
        await asyncio.gather(*tasks)


async def loop(settings: Settings) -> None:
    """Run the orchestrator tick loop until cancelled."""

    logging.basicConfig(level=settings.orchestrator.log_level)
    project_root = Path(settings.orchestrator.project_root)
    inboxes = []
    for project in settings.projects:
        inbox_pattern = project_root / project / settings.orchestrator.inbox_glob
        outbox_dir = (
            project_root
            / project
            / settings.orchestrator.outbox_dir_name
        )
        inboxes.append(
            Mailbox(
                inbox_pattern,
                outbox=outbox_dir,
                glob_mode=True,
            )
        )

    while True:
        await tick(inboxes)
        await asyncio.sleep(settings.orchestrator.loop_interval_seconds)


def run() -> None:
    """Load settings and run the orchestrator loop."""

    settings = load_settings()
    asyncio.run(loop(settings))


if __name__ == "__main__":
    run()
