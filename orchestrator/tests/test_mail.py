from datetime import datetime

from orchestrator.mail import Mailbox
from orchestrator.models import MailThread


def test_mailbox_yields_only_new_threads(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    thread_path = inbox / "glp1-companion__architect.md"
    thread_path.write_text("# Hello\nFirst draft", encoding="utf-8")

    mailbox = Mailbox(inbox)

    first_pass = list(mailbox.inbox_threads())
    assert len(first_pass) == 1
    assert isinstance(first_pass[0], MailThread)

    second_pass = list(mailbox.inbox_threads())
    assert second_pass == []

    thread_path.write_text("# Hello\nUpdated draft", encoding="utf-8")

    third_pass = list(mailbox.inbox_threads())
    assert len(third_pass) == 1
    assert "Updated" in third_pass[0].body


def test_mail_thread_metadata_from_filename(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    thread_path = inbox / "glp1-companion__qa.md"
    thread_path.write_text("Body", encoding="utf-8")

    thread = MailThread.from_path(thread_path)

    assert thread.project == "glp1-companion"
    assert thread.agent == "qa"
    assert isinstance(thread.updated_at, datetime)
    assert thread.updated_at.tzinfo is not None
    assert thread.summary() == "Body"
    assert thread.reply_filename().startswith("glp1-companion__qa")
